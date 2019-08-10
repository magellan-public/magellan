from .dataplane import *
from .datastore_proxy import DatastoreProxy

def extract_ports(spStr):
    temp = spStr.replace("shortestPath", "")
    temp = temp.replace("(", "")
    temp = temp.replace(")", "")
    src_port, dst_port = temp.split(",")
    return src_port, dst_port


class FlowRulesGenerator:
    def __init__(self, dsProxy):
        self.dsProxy = dsProxy
        self.existingPITs = {} # portTag -> pit

        self.topology = self.dsProxy.get_topo()

        self.dataplane = {} # port: pipeline

        self.vlanPath = 0

    # pit: a list of tables
    def accept_new_pit(self, portTag, pit):
        ports = self.topology.get_ports_with_tag(portTag)

        for port in ports:
            pipeline = Pipeline(pit)
            self.dataplane[port] = pipeline

            self.update_tagged_port(port, portTag, pipeline)
            self.update_action(pipeline)

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
                for idx, action in enumerate(flowrule.actions):
                    # print(str(action))
                    if action.type == TERMINAL_ACTION and 'shortestPath' in action.action:
                        src_port, dst_port = extract_ports(action.action)
                        # print(str(action))
                        if src_port == dst_port:
                            remove = True
                            break
                        sp = self.topology.shortestPath_full(src_port, dst_port)
                        flowrule.actions[idx] = sp
                if remove:
                    pipelineTable.flowRules.remove(flowrule)



    def dump(self):
        for port in self.dataplane:
            print("port: " + str(port))
            self.dataplane[port].dump()




