from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, ofproto_v1_3_parser
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.hub import spawn, sleep
import json
import os


class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.ds = {"global_mac_table": {}}
        spawn(self._start)

    def _start(self):
        sleep(4)
        self.recompile()

    def recompile(self):
        global_mac_table = self.ds['global_mac_table']
        for dpid in self.mac_to_port:
            for mac in self.mac_to_port[dpid]:
                sw = "s"+str(dpid)
                global_mac_table[mac] = sw + ':' + str(self.mac_to_port[dpid][mac])

        dir_path = os.path.dirname(os.path.abspath(__file__))
        with open(dir_path + '/ds.json', 'w') as fp:
            fp.write(json.dumps(self.ds))

        path = dir_path
        for i in range(3):
            path = os.path.dirname(path)
        os.system('sudo python3 ' + path + '/main.py')

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        assert isinstance(msg, ofproto_v1_3_parser.OFPPacketIn)
        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        inport = msg.match['in_port']
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, inport)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = inport

        return self.recompile()

        # if dst in self.mac_to_port[dpid]:
        #     out_port = self.mac_to_port[dpid][dst]
        # else:
        #     out_port = ofproto.OFPP_FLOOD
        #
        # actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        #
        # # install a flow to avoid packet_in next time
        # if out_port != ofproto.OFPP_FLOOD:
        #     self.add_flow(datapath, msg.in_port, dst, src, actions)
        #
        # data = None
        # if msg.buffer_id == ofproto.OFP_NO_BUFFER:
        #     data = msg.data
        #
        # out = datapath.ofproto_parser.OFPPacketOut(
        #     datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
        #     actions=actions, data=data)
        # datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illeagal port state %s %s", port_no, reason)
