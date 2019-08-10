import json
import networkx as nx


def generate_graph(jsonFile):
    with open(jsonFile) as json_file:
        data = json.load(json_file)
    return data


# add edges
def initialize_dg(dg, topo):
    links = topo['links']
    for link in links:
        src_port_id = link['source']
        dst_port_id = link['destination']
        src_node = src_port_id.split(':')[0]
        dst_node = dst_port_id.split(':')[0]
        dg.add_edge(src_node, dst_node)


def initialize_g(g, topo):
    links = topo['links']
    added_edge = []
    for link in links:
        link_id = link['id']
        if link_id not in added_edge:
            src_port_id = link['source']
            dst_port_id = link['destination']
            src_node = src_port_id.split(':')[0]
            dst_node = dst_port_id.split(':')[0]
            g.add_edge(src_node, dst_node)
            added_edge.append(link_id)
            rv_link_id = dst_port_id + '-' + src_port_id
            added_edge.append(rv_link_id)


# add edges
def initialize_full_dg(fullDg, topo):
    links = topo['links']
    for link in links:
        src_port_id = link['source']
        dst_port_id = link['destination']
        src_node = src_port_id.split(':')[0]
        dst_node = dst_port_id.split(':')[0]
        fullDg.add_edge(src_port_id, dst_port_id)
        fullDg.add_edge(src_node, src_port_id)
        fullDg.add_edge(dst_port_id, dst_node)


def initialize_full_g(fullG, topo):
    links = topo['links']
    added_edge = []
    for link in links:
        link_id = link['id']
        if link_id not in added_edge:
            src_port_id = link['source']
            dst_port_id = link['destination']
            src_node = src_port_id.split(':')[0]
            dst_node = dst_port_id.split(':')[0]
            fullG.add_edge(src_port_id, dst_port_id)
            fullG.add_edge(src_node, src_port_id)
            fullG.add_edge(dst_port_id, dst_node)
            added_edge.append(link_id)
            rv_link_id = dst_port_id + '-' + src_port_id
            added_edge.append(rv_link_id)


class Topology:
    def __init__(self, jsonFile):
        self.topo = generate_graph(jsonFile)
        self.dg = nx.DiGraph()
        self.g = nx.Graph()
        initialize_dg(self.dg, self.topo)
        initialize_g(self.g, self.topo)

        self.fullDg = nx.DiGraph()
        self.fullG = nx.Graph()
        initialize_full_dg(self.fullDg, self.topo)
        initialize_full_g(self.fullG, self.topo)


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

    def get_single_link_id(self, src_sw, dst_sw):
        links = self.topo['links']
        for link in links:
            src_port_id = link['source']
            dst_port_id = link['destination']
            src_sw_compare = src_port_id.split(':')[0]
            dst_sw_compare = dst_port_id.split(':')[0]
            if src_sw == src_sw_compare and dst_sw == dst_sw_compare:
                return link['id']

    def shortestPath_nodes(self, src_port, dst_port):
        src_node = src_port.split(':')[0]
        dst_node = dst_port.split(':')[0]
        sp = nx.shortest_path(self.dg, src_node, dst_node)
        return sp

    def shortestPath_full(self, src_port, dst_port):
        sp = nx.shortest_path(self.fullDg, src_port, dst_port)
        return sp


    def stp_edges(self):
        edges = nx.minimum_spanning_edges(self.g)
        return list(edges)

    def path_in_stp(self, src_port, dst_port):
        tree = nx.minimum_spanning_tree(self.g)
        src_node = src_port.split(':')[0]
        dst_node = dst_port.split(':')[0]
        sp = nx.shortest_path(tree, src_node, dst_node)
        return sp


if __name__ == '__main__':
    topology = Topology("../topologies/l2.json")
    print(topology.path_in_stp('s1:1', 'h2:1'))