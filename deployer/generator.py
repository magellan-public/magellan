from .dataplane import *
from .simple_vlan_dataplane import *


def extract_ports(spStr):
    temp = spStr.replace("shortestPath", "")
    temp = temp.replace("(", "")
    temp = temp.replace(")", "")
    src_port, dst_port = temp.split(",")
    return src_port, dst_port


def extract_port_stp(stpStr):
    temp = stpStr.replace("spanningTree", "")
    temp = temp.replace("(", "")
    temp = temp.replace(")", "")
    return temp


def construct_vlan_action(vlanId):
    return ("set_vlan", vlanId)


def construct_outport_action(outport):
    return ("output",  outport)


class FlowRulesGenerator:
    def __init__(self, dsProxy):
        self.dsProxy = dsProxy
        self.existingPITs = {} # portTag -> pit

        self.topology = self.dsProxy.get_topo()

        self.dataplane = {} # port: pipeline

        self.vlanId = 100

        self.vlanPath = {}

    # pit: a list of tables
    def accept_new_pit(self, portTag, pit):
        ports = self.topology.get_ports_with_tag(portTag)

        for port in ports:
            pipeline = Pipeline(pit)
            self.dataplane[port] = pipeline

            self.update_tagged_port(port, portTag, pipeline)
            self.update_action(pipeline)
            self.remove_redundant_flowrule_with_inport(pipeline, port)
    
    def remove_redundant_flowrule_with_inport(self, pipeline, port):
        for pipelineTable in pipeline.pipelineTables:
            for flowrule in pipelineTable.flowRules[:]:
                if 'inport' in flowrule.matches:
                    value = flowrule.matches['inport']
                    if str(value) != str(port) and str(value)!="*":
                        pipelineTable.flowRules.remove(flowrule)

    def update_tagged_port(self, port, tag, pipeline):
        for pipelineTable in pipeline.pipelineTables:
            for flowrule in pipelineTable.flowRules:
                for match in flowrule.matches:
                    if match == 'inport_label' and flowrule.matches[match] == tag:
                        flowrule.matches[match] = port

    def update_action(self, pipeline):
        for pipelineTable in pipeline.pipelineTables:
            for flowrule in pipelineTable.flowRules[:]:
                remove = False
                for idx0, action in enumerate(flowrule.actions):
                    # print(str(action))
                    if action.type == TERMINAL_ACTION and 'shortestPath' in action.action:
                        src_port, dst_port = extract_ports(action.action)
                        # print(str(action))
                        if src_port == dst_port:
                            remove = True
                            break
                        sp = self.topology.shortestPath_full(src_port, dst_port)
                        for idx, port_or_node in enumerate(sp):
                            if ":" not in port_or_node:
                                if idx == 1:  # skip first node
                                    continue
                                port = sp[idx-1]
                                outport = sp[idx+1]
                                isLast = False
                                if idx == len(sp)-2:
                                    isLast = True
                                if port not in self.dataplane:
                                    vlanTable = VlanTable(port)
                                    vlanTable.add_flow_rule(self.vlanId, [outport], isLast)
                                    self.dataplane[port] = vlanTable
                                else:
                                    vlanTable = self.dataplane[port]
                                    vlanTable.add_flow_rule(self.vlanId, [outport], isLast)

                        # flowrule.actions[idx0] = sp
                        flowrule.actions[idx0] = [construct_vlan_action(self.vlanId), construct_outport_action(sp[2])]
                        self.vlanId += 1
                        # flowrule.actions[idx0] = construct_vlan_outport(self.vlanId, sp[2])
                    elif action.type == TERMINAL_ACTION and 'spanningTree' in action.action:
                        src_port = extract_port_stp(action.action)
                        for port in self.topology.get_external_ports():
                            if port == src_port:
                                continue
                            else:
                                sp = self.topology.path_in_stp_full(src_port, port)
                                # print(sp)

                                for idx, port_or_node in enumerate(sp):
                                    if ":" not in port_or_node:
                                        if idx == 1:  # skip first node
                                            continue
                                        port = sp[idx - 1]
                                        outport = sp[idx + 1]
                                        isLast = False
                                        if idx == len(sp) - 2:
                                            isLast = True
                                        if port not in self.dataplane:
                                            vlanTable = VlanTable(port)
                                            vlanTable.add_flow_rule(self.vlanId, [outport], isLast)
                                            self.dataplane[port] = vlanTable
                                        else:
                                            vlanTable = self.dataplane[port]
                                            vlanTable.add_flow_rule(self.vlanId, [outport], isLast)

                                # flowrule.actions[idx0] = sp
                                flowrule.actions[idx0] = [construct_vlan_action(self.vlanId),
                                                          construct_outport_action(sp[2])]
                                self.vlanId += 1

                if remove:
                    pipelineTable.flowRules.remove(flowrule)

    def dump(self):
        for port in self.dataplane:
            print("port: " + str(port))
            self.dataplane[port].dump()

    def get_per_switch_config(self):
        per_switch_config = {} # type: {str: {}}
        for sw in self.topology.get_switches():
            per_switch_config.setdefault(sw['id'], {}) # TODO
        for sw_port, pipe in self.dataplane.items():
            sw, port = sw_port.split(":")
            per_switch_config.setdefault(sw, {})
            table_map = per_switch_config.get(sw)
            if isinstance(pipe, Pipeline):
                for t in pipe.pipelineTables:
                    if isinstance(t, PipelineTable):
                        t1 = table_map.get(t.tableId)
                        if t1 is None:
                            table_map[t.tableId] = t
                        else:
                            assert t1.matches == t.matches
                            t1.flowRules.extend(t.flowRules)
            elif isinstance(pipe, VlanTable):
                t = pipe
                t1 = table_map.get(-1)  # type: PipelineTable
                if t1 is None:
                    t1 = PipelineTable(-1, None, None, None)
                    table_map[-1] = t1
                    t1.matches = ["inport", "vlan"]
                    # t1.actions = ["vlan_output"]
                    # flow = FlowRule({"pri":0}, None, None, None, None)
                    # flow.matches = {}
                    # flow.actions = []
                    # t1.flowRules.append(flow)
                for vlanId, action in t.matches.items():
                    flow = FlowRule({"pri":1}, None, None, None, None)
                    flow.matches = {"inport": sw_port, "vlan":vlanId}
                    flow.actions = [('vlan_output', action)]
                    t1.flowRules.append(flow)
        return per_switch_config

