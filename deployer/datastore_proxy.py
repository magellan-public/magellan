"""
This module should connect to datastore to get data e.g., topology
"""
from topology import topology

class datastoreProxy:
    def __init__(self, topoJson):
        self.topoJson = topoJson


    def get_topo(self):
        #topo = topology('D:/CZU/PengCheng/magellan-pcl/topologies/' + self.topoJson)
        topo = topology('../topologies/' + self.topoJson)
        return topo

if __name__ == '__main__':
    ds = datastoreProxy('l2.json')
    topo = ds.get_topo()
    #print(topo.get_host_ports())
    print(topo.get_external_ports())

