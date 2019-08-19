// this is generated automatically

#include <core.p4>
#include <v1model.p4>

header ethernet_t {
    bit<48> dst;
    bit<48> src;
    bit<16> etherType;
}

header tag_t{
    bit<16> tag;
    bit<16> innerEthType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  ctrl;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

struct metadata {
    {% for var in variables %}bit<{{var.len}}> {{var.name}};
    {% endfor %}bool terminal;
}

@controller_header("packet_in")
header packet_in_header_t {
    bit<9> ingress_port;
    bit<7> _padding;
}

struct headers {
    ethernet_t ethernet;
    tag_t      tag;
    ipv4_t     ipv4;
    tcp_t      tcp;
    packet_in_header_t packet_in;
}

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }
    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x800: parse_ipv4;
            0xffff: parse_tag;
            default: accept;
        }
    }

    state parse_tag {
        packet.extract(hdr.tag);
        transition select(hdr.tag.innerEthType) {
            0x800: parse_ipv4;
            // 0xffff: reject;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            6: parse_tcp;
            default: accept;
        }
    }
    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action output(bit<9> port){
        standard_metadata.egress_spec = port;
    }

    action controller(){
        standard_metadata.egress_spec = 100;
        hdr.packet_in.setValid();
        hdr.packet_in.ingress_port = standard_metadata.ingress_port;
    }

    action set_terminal(){
        meta.terminal = true;
    }

    action push_tag_output(bit<16> tag, bit<9> port){
        hdr.tag.setValid();
        hdr.tag.tag = tag;
        hdr.tag.innerEthType = hdr.ethernet.etherType;
        hdr.ethernet.etherType = 0xffff;
        standard_metadata.egress_spec = port;
    }

    action pop_tag_output(bit<9> port){
        hdr.tag.setInvalid();
        hdr.ethernet.etherType = hdr.tag.innerEthType;
        standard_metadata.egress_spec = port;
    }

    {% for table in tables %}
    action {{table.name}}_action({{table.action_parm_str}}) {
        {{table.action_str}}
    }
    {% endfor %}
    {% for table in tables %}
    table {{ table.name }} {
        key = {
            {% for match in table.matches %}{{match.name}}: {{match.type}};
            {% endfor %}
        }
        actions = { {{table.name}}_action; NoAction;}
        const default_action = NoAction; // defined in core.p4
        size = 65536;
    }
    {% endfor %}
    apply {
        meta.terminal = false;
        if (hdr.ethernet.isValid()) {
            {% for table in tables %}if(!meta.terminal){{table.name}}.apply();
            {% endfor %}if(!meta.terminal)drop();
        } else {
            drop();
        }
    }
}

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {}
}

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply {
    update_checksum(
        hdr.ipv4.isValid(),
            { hdr.ipv4.version,
          hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.packet_in);
        packet.emit(hdr.ethernet);
        packet.emit(hdr.tag);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.tcp);
    }
}

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;