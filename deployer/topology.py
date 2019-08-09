import json
import networkx as nx

def generate_graph(jsonFile):
    with open(jsonFile) as json_file:
        data = json.load(json_file)
    return data

class topology:
    def __init__(self, jsonFile):
        self.topo = generate_graph(jsonFile)

    def get_switches(self):
        nodes = self.topo['nodes']
        switches = []
        for node in nodes:
            if node['type'] == 'switch':
                id = node['id']
                ports = list(node['ports'])
                switch = {}
                switch['id'] = id
                switch['ports'] = ports
                switches.append(switch)
        return switches

    def get_sw_ports(self):
        nodes = self.topo['nodes']
        ports = []
        for node in nodes:
            if node['type'] == 'switch':
                node_ports = node['ports']
                for p in node_ports:
                    ports.append(p)
        return ports

    def get_host_ports(self):
        nodes = self.topo['nodes']
        ports = []
        for node in nodes:
            if node['type'] == 'host':
                node_ports = node['ports']
                for p in node_ports:
                    ports.append(p)
        return ports

    def get_external_ports(self):
        host_ports = self.get_host_ports()
        links = self.topo['links']
        external_ports = []
        for host_port in host_ports:
            for link in links:
                if link['source'] == host_port:
                    external_ports.append(link['destination'])
        return external_ports

    def get_ports_with_tag(self, tag):
        ports = self.topo['ports']
        ports_tag = []
        for port in ports:
            if port['tag'] == tag:
                ports_tag.append(port['id'])
        return ports_tag


if __name__ == '__main__':
    topology = topology("../topologies/l2.json")
    print(topology.get_ports_with_tag('external_ingress'))