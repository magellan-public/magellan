"""
This module should connect to datastore to get data e.g., topology
"""
from topology import Topology


class DatastoreProxy:
    def __init__(self, topoJson):
        self.topoJson = topoJson


    def get_topo(self):
        topo = Topology('../topologies/' + self.topoJson)
        return topo

if __name__ == '__main__':
    ds = DatastoreProxy('l2.json')
    topo = ds.get_topo()
    #print(topo.get_host_ports())
    print(topo.get_external_ports())

