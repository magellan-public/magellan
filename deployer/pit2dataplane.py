from .dataplane import *
from .datastore_proxy import DatastoreProxy

class FlowRulesGenerator:
    def __init__(self, dsProxy):
        self.dsProxy = dsProxy
        self.existingPITs = {} # portTag -> pit

        self.topology = self.dsProxy.get_topo()

        self.dataplane = {} # port: pipeline

    # pit: a list of tables
    def accept_new_pit(self, portTag, pit):
        ports = self.topology.get_ports_with_tag(portTag)

        for port in ports:
            pipeline = Pipeline(pit)
            self.dataplane[port] = pipeline

    def dump(self):
        for port in self.dataplane:
            print("port: " + str(port))
            self.dataplane[port].dump()




