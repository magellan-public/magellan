import os
import re

import deployer.dataplane
from deployer.dataplane import PipelineTable, FlowRule, GlobalAction
from utils.utils import error


class OpenFlowAdapter:
    def __init__(self):
        pass

    def update(self, per_switch_config):
        for sw, pipe in per_switch_config.items():
            self._update_sw(sw, pipe)

    def _update_sw(self, sw, pipe):
        self._delete_all(sw)
        for tid, table in pipe.items(): # type: int, PipelineTable
            for f in table.flowRules: # type: FlowRule
                f.priority+=10
                self._install_flow(sw, tid+1, f)
            self._install_flow(sw, tid+1, FlowRule({"pri":0}, None, None, None, None))

    def _system_cmd(self, cmd):
        print(cmd)
        if os.getuid()==0:
            os.system(cmd)
        else:
            print("no permission")

    def _delete_all(self, sw):
        self._system_cmd("ovs-ofctl del-flows %s"%sw)

    def _install_flow(self, sw, tid, flow):
        # flow.dump()
        priority, matches, actions = self._convert(flow, tid + 1)
        matches_str = ','.join(str(f)+"="+str(v) for f,v in matches.items())
        actions_str = ','.join(actions)
        self._system_cmd("ovs-ofctl add-flow %s -OOpenFlow13 \"table=%d, priority=%d, %s, actions=%s\"" %(sw, tid, priority, matches_str, actions_str))

    def _convert(self, flow, next_table):
        matches = {}
        actions = []
        for field, value in flow.matches.items():
            assert isinstance(field, str)
            if value == '*':
                continue
            if field == 'inport_label' or field=='inport':
                matches['in_port'] = self._convert_sw_port(value)
            elif field == 'vlan':
                matches['dl_vlan'] = value
            elif field == 'pkt.eth.src':
                matches['eth_src'] = value
            elif field == 'pkt.eth.dst':
                matches['eth_dst'] = value
            else:
                reg = self._convert_reg(field)
                if reg:
                    matches[reg] = value
                else:
                    error("unknown field", field)
        isterminal = False
        for act in flow.actions:
            if isinstance(act, GlobalAction):
                if act.type == deployer.dataplane.NON_TERMINAL_ACTION:
                    reg = self._convert_reg(act.key)
                    if not reg:
                        error("unknown field", act.key)
                    actions.append("set_field:%s->%s"%(act.value,reg))
                elif act.action == 'toController':
                    actions.append("controller:65535")
                    isterminal = True
                else:
                    error("unknown action", act, act.action)
            elif isinstance(act, list):
                for act2 in act:
                    actions.extend(self._convert_act(act2))
                    isterminal = True # TODO
            elif isinstance(act, tuple):
                actions.extend(self._convert_act(act))
                isterminal = True # TODO
            else:
                error("unknown action type")
        if not isterminal:
            actions.append("goto_table:"+str(next_table))
        return flow.priority, matches, actions

    def _convert_act(self, act):
        type = act[0]
        ret = []
        if type=='vlan_output':
            sw_port, isfinal = act[1]
            if isfinal:
                ret.append('pop_vlan')
            output = ','.join(str(p) for p in self._convert_output_ports(sw_port))
            ret.append('output:' + output)
        elif type=='set_vlan':
            ret.append('push_vlan:0x8100,mod_vlan_vid:%s'%str(act[1]))
        elif type=='output':
            output=','.join(str(p) for p in self._convert_output_ports(act[1]))
            ret.append('output:' + output)
        else:
            error('unknown action')
        return ret

    def _convert_output_ports(self, ports):
        if isinstance(ports, list) or isinstance(ports, tuple):
            return [self._convert_sw_port(p) for p in ports]
        elif isinstance(ports, str):
            return [self._convert_sw_port(ports)]
        else:
            error("error port format")

    def _convert_sw_port(self, port):
        try:
            sw, port = port.split(':')
        except ValueError:
            error(port)
        return int(port)

    def _convert_reg(self, reg):
        mat = re.match(r'r(\d+)', reg)
        if mat:
            regnum = int(mat.group(1))
            if regnum > 15:
                return None
            return 'reg'+str(regnum)
        return None