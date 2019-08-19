#!/usr/bin/env python3
import argparse
import grpc
import os
import sys
import json
import queue
import struct
from time import sleep

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../'))

from main import Compiler
import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper

SWITCH_TO_HOST_PORT = 1
SWITCH_TO_SWITCH_PORT = 2


def to_hex(t, width):
    a = hex(t)[2:]
    l = width - len(a)
    if l>0:
        return '0'*l + a
    else:
        return a[-width:]


def parse_mac(b):
    a = struct.unpack('BBBBBB', b)
    return ":".join(to_hex(i, 2) for i in a)


def writeTunnelRules(p4info_helper, ingress_sw, egress_sw, tunnel_id,
                     dst_eth_addr, dst_ip_addr):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.myTunnel_ingress",
        action_params={
            "dst_id": tunnel_id,
        })
    ingress_sw.WriteTableEntry(table_entry)
    print("Installed ingress tunnel rule on %s" % ingress_sw.name)

    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={
            "hdr.myTunnel.dst_id": tunnel_id
        },
        action_name="MyIngress.myTunnel_forward",
        action_params={
            "port": SWITCH_TO_SWITCH_PORT
        })
    ingress_sw.WriteTableEntry(table_entry)
    print("Installed transit tunnel rule on %s" % ingress_sw.name)

    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={
            "hdr.myTunnel.dst_id": tunnel_id
        },
        action_name="MyIngress.myTunnel_egress",
        action_params={
            "dstAddr": dst_eth_addr,
            "port": SWITCH_TO_HOST_PORT
        })
    egress_sw.WriteTableEntry(table_entry)
    print("Installed egress tunnel rule on %s" % egress_sw.name)


def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print('\n----- Reading tables rules for %s -----' % sw.name)
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs in the entry to names
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print('%s: ' % table_name, end=' ')
            for m in entry.match:
                print(p4info_helper.get_match_field_name(table_name, m.field_id), end=' ')
                print('%r' % (p4info_helper.get_match_field_value(m),), end=' ')
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print('->', action_name, end=' ')
            for p in action.params:
                print(p4info_helper.get_action_param_name(action_name, p.param_id), end=' ')
                print('%r' % p.value, end=' ')
            print()


def printCounter(p4info_helper, sw, counter_name, index):
    """
    Reads the specified counter at the specified index from the switch. In our
    program, the index is the tunnel ID. If the index is 0, it will return all
    values from the counter.

    :param p4info_helper: the P4Info helper
    :param sw:  the switch connection
    :param counter_name: the name of the counter from the P4 program
    :param index: the counter index (in our case, the tunnel ID)
    """
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            print("%s %s %d: %d packets (%d bytes)" % (
                sw.name, counter_name, index,
                counter.data.packet_count, counter.data.byte_count
            ))


def printGrpcError(e):
    print("gRPC Error:", e.details(), end=' ')
    status_code = e.code()
    print("(%s)" % status_code.name, end=' ')
    traceback = sys.exc_info()[2]
    print("[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno))


class SwitchManager:
    def __init__(self, name, address, id, tmpdir):
        self._name = name # type: str
        self._address = address
        self._id = id # type: int
        self._conn = None
        self._tmp_dir = tmpdir
        self._p4_md5 = ""
        self._p4info_helper = None

    def get_name(self):
        return self._name

    def connect(self, msg_queue):
        self._conn = p4runtime_lib.bmv2.Bmv2SwitchConnection(
                name=self._name,
                address=self._address,
                device_id=self._id,
                proto_dump_file=self._tmp_dir + 'log-%s-p4runtime-requests.txt'%self._name)
        self._conn.MasterArbitrationUpdate()
        self._conn.start(self._id, msg_queue)

    def update_pipeline(self, p4_md5):
        if p4_md5!= self._p4_md5:
            self._p4_md5 = p4_md5
            p4info_file_path = self._tmp_dir +  "pipe-%s.p4.info.txt" % p4_md5
            bmv2_file_path = self._tmp_dir + "pipe-%s.p4.json" % p4_md5
            if not os.path.exists(p4info_file_path):
                p4_file_path = self._tmp_dir + "pipe-%s.p4" % p4_md5
                os.system("p4c-bm2-ss --p4v 16 --p4runtime-files %s -o %s %s"%(p4info_file_path, bmv2_file_path, p4_file_path))
            self._p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)
            self._conn.SetForwardingPipelineConfig(p4info=self._p4info_helper.p4info,
                                            bmv2_json_file_path=bmv2_file_path)
        else:
            self._conn.DeleteAllTableEntry()
        with open(self._tmp_dir + "runtime-%s.json"%self._name) as f:
            rules = json.load(f)
            for tname, entries in rules.items():
                for entry in entries:
                    # print(entry)
                    table_entry = self._p4info_helper.buildTableEntry(
                        priority=int(entry["priority"])+1,
                        table_name="MyIngress.%s"%tname,
                        match_fields=entry["matches"],
                        action_name="MyIngress.%s"%entry["action_name"],
                        action_params=entry["action_params"])
                    self._conn.WriteTableEntry(table_entry)

    def parse_packet_ingress(self, pkt):
        for p in self._p4info_helper.p4info.controller_packet_metadata:
            for m in p.metadata:
                if m.name == "ingress_port":
                    print(pkt)
                    for md in pkt.metadata:
                        if md.metadata_id == m.id:
                            return struct.unpack_from("!H", md.value)[0]
        raise AssertionError("ingress port not found")


class Controller:
    def __init__(self, source_file, topo_file, tmpdir = '/tmp/magellan/', ):
        self._topo = json.load(open(topo_file))
        self._msg_queue = queue.Queue()
        self._sw_mgr = {}
        self._sw_name_to_mgr = {}
        self._tmp_dir = tmpdir
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        self._compiler = Compiler(source_file, topo_file, tmpdir)
        self._datastore = {"global_mac_table": {}}

    def run(self):
#        try:
        self._connect()
        self._compiler.compile_ast()
        self._update()
        while True:
            id, msg = self._msg_queue.get()
            if msg.packet:
                self._on_packet(msg.packet, id)
        # except KeyboardInterrupt:
        #     print(" Shutting down.")
        # except grpc.RpcError as e:
        #     printGrpcError(e)
        ShutdownAllSwitchConnections()

    def _connect(self):
        device_id = 0
        for n in self._topo["nodes"]:
            if n["type"]=="switch":
                id = n["id"]
                addr = n["address"]
                mgr = SwitchManager(id, addr, device_id, self._tmp_dir)
                self._sw_name_to_mgr[id] = self._sw_mgr[device_id] = mgr
                mgr.connect(self._msg_queue)
                device_id += 1

    def _update(self):
        self._compiler.compile_result(self._datastore)
        with open(self._tmp_dir + "sw_p4.json") as f:
            p4_file_md5 = json.load(f)
            for sw, md5 in p4_file_md5.items():
                self._sw_name_to_mgr[sw].update_pipeline(md5)

    def _on_packet(self, pkt, sw_id):
        dst, src, ethertype = struct.unpack_from('!6s6sH', pkt.payload)
        dst_mac = parse_mac(dst)
        src_mac = parse_mac(src)
        print(src_mac, dst_mac, ethertype)
        inport = self._sw_mgr[sw_id].parse_packet_ingress(pkt)
        mt = self._datastore["global_mac_table"]
        if src_mac not in mt:
            name = self._sw_mgr[sw_id].get_name()
            mt[src_mac]= "%s:%d"%(name, inport)
            print(mt)
            self._update()

#
# def main():
#     try:
#         sw_l = []
#         p4info_helper_l = []
#         q = queue.Queue()
#         for i in range(5):
#             sw_l.append(p4runtime_lib.bmv2.Bmv2SwitchConnection(
#                 name='s%d'%(i+1),
#                 address='172.17.0.2:%d'%(50051+i),
#                 device_id=i,
#                 proto_dump_file='logs/s%d-p4runtime-requests.txt'%(i+1)))
#             sw_l[i].MasterArbitrationUpdate()
#             sw_l[i].start(i, q)
#
#             p4info_file_path = "pipe/pipe-s%d.p4.info.txt"%(i+1)
#             bmv2_file_path = "pipe/pipe-s%d.p4.json"%(i+1)
#             p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)
#             sw_l[i].SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
#                                                  bmv2_json_file_path=bmv2_file_path)
#             p4info_helper_l.append(p4info_helper)
#
#             with open("pipe/runtime-s%d.json"%(i+1)) as f:
#                 rules = json.load(f)
#                 # rules = byteify(rules)
#                 for tname, entries in rules.items():
#                     for entry in entries:
#                         print(entry)
#                         table_entry = p4info_helper.buildTableEntry(
#                             priority=int(entry["priority"])+1,
#                             table_name="MyIngress.%s"%tname,
#                             match_fields=entry["matches"],
#                             action_name="MyIngress.%s"%entry["action_name"],
#                             action_params=entry["action_params"])
#                         sw_l[i].WriteTableEntry(table_entry)
#
#         for i in range(5):
#             readTableRules(p4info_helper_l[i], sw_l[i])
#
#         # sleep(10)
#         # for i in range(5):
#         #     sw_l[i].DeleteAllTableEntry()
#
#         while True:
#             id, msg = q.get()
#             print(msg)
#             dst, src, ethertype = struct.unpack_from('!6s6sH', msg.packet.payload)
#             print((parse_mac(dst)))
#             print((parse_mac(src)))
#             print(ethertype)
#             print((parse_packet_ingress(p4info_helper_l[id], msg.packet)))
#
#     except KeyboardInterrupt:
#         print(" Shutting down.")
#     except grpc.RpcError as e:
#         printGrpcError(e)
#
#     ShutdownAllSwitchConnections()


if __name__ == '__main__':
    Controller("../apps/l2/on_packet.mag", "../topology/l2-p4.json").run()