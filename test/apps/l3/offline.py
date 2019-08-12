import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from magellan import *

port_to_ip = {
  'r1:1': '10.0.0.1',
  'r1:2': '192.168.1.1',
  'r1:3': '172.16.1.1'
}
port_to_mac = {
  'r1:1': '00:00:00:00:00:01',
  'r1:2': '00:00:00:00:00:02',
  'r1:3': '00:00:00:00:00:03'
}

def handle_arp(pkt, inport):
  ip_to_mac = get('ip_to_mac')
  ip_to_mac.set(pkt.arp.sender_ip, pkt.arp.sender_mac, 4 * 3600)
  set('ip_to_mac', ip_to_mac)
  if pkt.arp.target_ip == port_to_ip[inport] and pkt.arp.opcode == 1:
    new_pkt = new_packet('ARP', {
      'eth.src': port_to_mac[inport],
      'eth.dst': pkt.arp.sender_mac,
      'arp.opcode': 2,
      'arp.target_mac': pkt.arp.sender_mac,
      'arp.target_ip': pkt.arp.sender_ip,
      'arp.sender_mac': port_to_mac[inport],
      'arp.sender_ip': pkt.arp.target_ip
    })
    send_packet(new_pkt, inport)

def handle_ip_to_mac_miss(pkt, port):
  arp_request = new_packet('ARP', {
    'eth.src': port_to_mac[port],
    'eth.dst': '0xffffffffffff',
    'arp.opcode': 1,
    'arp.target_mac': '0x000000000000',
    'arp.target_ip': pkt.ipv4.dst,
    'arp.sender_mac': port_to_mac[port],
    'arp.sender_ip': port_to_ip[port]
  })
  send_packet(arp_request, port)

