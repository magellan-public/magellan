import re
import json

from jinja2 import Template

import deployer.dataplane
from deployer.dataplane import PipelineTable, FlowRule, GlobalAction
from utils.utils import error


class P4Adapter:
    def __init__(self, template_file, result_dir = '/tmp/'):
        self._template_file = template_file
        self._sw_config_index = {} # swid -> index
        self._configs = {}  # index -> config
        self._result_dir = result_dir

    def update(self, per_switch_config):
        for sw, pipe in per_switch_config.items():
            self._update_sw(sw, pipe)

    def _update_sw(self, sw, pipe):
        print('==================', sw)
        for tid, table in sorted(pipe.items()): # type: int, PipelineTable
            table.dump()
        self._gen_p4(sw, pipe)

    def _gen_p4(self, sw, pipe):
        tables = []
        variables = set()
        sw_flows = {}
        for tid, table in sorted(pipe.items()): # type: int, PipelineTable
            matches, regs, action_parm_str, action_str, flows = self._parse_table(table)
            sw_flows['t%d'%(tid+1)]=flows
            data = {'name': 't' + str(tid+1),
                'matches': matches,
                'action_parm_str': action_parm_str,
                'action_str': action_str,
                'size' : 65536}
            tables.append(data)
            variables.update(regs)
        variables = [{'name': n, 'len':2} for n in variables]
        with open(self._template_file) as f, open(self._result_dir + 'pipe-%s.p4'%str(sw),'w') as f2:
            template = Template(f.read())
            result = template.render(tables=tables, variables=variables)
            f2.write(result)
        with open(self._result_dir + 'runtime-%s.json'%str(sw),'w') as f:
            json.dump(sw_flows, f, indent=2)

    def _parse_table(self, table):
        TERNARY = 'ternary'
        EXACT = 'exact'
        table_headers = []
        regs = []
        for field in table.matches:
            if field=='pkt.eth.src':
                table_headers.append({'name': 'hdr.ethernet.src', 'type': TERNARY})
            elif field == 'pkt.eth.dst':
                table_headers.append({'name': 'hdr.ethernet.dst', 'type': TERNARY})
            elif field == 'pkt.eth.dst':
                table_headers.append({'name': 'hdr.ethernet.dst', 'type': TERNARY})
            elif field == 'inport_label' or field=='inport':
                table_headers.append({'name': 'standard_metadata.ingress_port', 'type': TERNARY})
            elif field == 'vlan':
                table_headers.append({'name': 'hdr.tag.tag', 'type': TERNARY})
            elif field =='pkt':

                pass
            else:
                reg = self._convert_reg(field)
                if reg:
                    regs.append(reg)
                    table_headers.append({'name': 'meta.'+reg, 'type': TERNARY})
                else:
                    error('unknown field', field)
        action_parm_str = ''
        action_str = ''
        if table.flowRules: # type: FlowRule
            _, _, actions = self._convert_flow(table.flowRules[0])
            ret = self._parse_action(actions)
            str_map = {
                'output': ('bit<9> port', 'output(port);'),
                'controller': ('','controller();'),
                'pop_tag_output': ('bit<9> port', 'pop_tag_output(port);'),
                'push_tag_output': ('bit<16> tag, bit<9> port', 'push_tag_output(tag, port);')
            }
            if ret[0] in str_map:
                action_parm_str, action_str = str_map[ret[0]]
            elif ret[0].startswith('set_field'):
                action_parm_str = 'bit<2> v'
                action_str = 'meta.%s = v;' % ret[0][9:]
            else:
                error('action error', ret)
        flows = []
        for f in table.flowRules:
            priority, matches, actions = self._convert_flow(f)
            ret = self._parse_action(actions)
            flows.append({
                'priority': priority,
                'matches': matches,
                'action_name': 't%d_action'%(table.tableId+1),
                'action_params': ret[1:]
            })
        return table_headers, regs, action_parm_str, action_str, flows

    def _parse_action(self, actions):
        if len(actions) == 1:
            a = actions[0]
            if a[0] == 'output':
                return 'output', a[1]
            elif a[0] == 'set_field':
                return 'set_field'+a[2], a[1]
            elif a[0] == 'controller':
                return 'controller',
            else:
                error('unhandled actions', actions)
        elif len(actions) == 2:
            a1, a2 = actions
            if a1[0] == 'pop_vlan' and a2[0] == 'output':
                return 'pop_tag_output', a2[1]
            elif a1[0] == 'set_vlan' and a2[0] == 'output':
                return 'push_tag_output', a1[1], a2[1]
            else:
                error('unhandled actions', actions)
        else:
            error('unhandled actions', actions)

    def _convert_flow(self, flow):
        matches = {}
        actions = []
        for field, value in flow.matches.items():
            assert isinstance(field, str)
            if value == '*':
                continue
            if field == 'inport_label' or field=='inport':
                matches['standard_metadata.ingress_port'] = self._convert_sw_port(value)
            elif field == 'vlan':
                matches['hdr.tag.tag'] = value
            elif field == 'pkt.eth.src':
                matches['hdr.ethernet.dst'] = value
            elif field == 'pkt.eth.dst':
                matches['hdr.ethernet.dst'] = value
            else:
                reg = self._convert_reg(field)
                if reg:
                    matches['meta.'+reg] = value
                else:
                    error('unknown field', field)
        isterminal = False
        for act in flow.actions:
            if isinstance(act, GlobalAction):
                if act.type == deployer.dataplane.NON_TERMINAL_ACTION:
                    reg = self._convert_reg(act.key)
                    if not reg:
                        error('unknown field', act.key)
                    actions.append(('set_field', act.value,reg))
                elif act.action == 'toController':
                    actions.append(('controller',))
                    isterminal = True
                else:
                    error('unknown action', act, act.action)
            elif isinstance(act, list):
                for act2 in act:
                    actions.extend(self._convert_act(act2))
                    isterminal = True # TODO
            elif isinstance(act, tuple):
                actions.extend(self._convert_act(act))
                isterminal = True # TODO
            else:
                error('unknown action type')
        return flow.priority, matches, actions

    def _convert_act(self, act):
        type = act[0]
        ret = []
        if type=='vlan_output':
            sw_port, isfinal = act[1]
            if isfinal:
                ret.append(('pop_vlan',))
            output = ','.join(str(p) for p in self._convert_output_ports(sw_port))
            ret.append(('output', output))
        elif type=='set_vlan':
            ret.append(('set_vlan', str(act[1])))
        elif type=='output':
            output=','.join(str(p) for p in self._convert_output_ports(act[1]))
            ret.append(('output', output))
        else:
            error('unknown action')
        return ret

    def _convert_output_ports(self, ports):
        if isinstance(ports, list) or isinstance(ports, tuple):
            return [self._convert_sw_port(p) for p in ports]
        elif isinstance(ports, str):
            return [self._convert_sw_port(ports)]
        else:
            error('error port format')

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