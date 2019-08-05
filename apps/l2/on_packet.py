macTable = {}  # mac -> port
STP = {}  # in_port -> Set of flood ports


def on_packet(pkt, in_port):

    macTable[pkt.eth.src] = in_port
    macTable.setTimeout(pkt.eth.src, 500)

    if pkt.eth.dst in macTable:
        return macTable[pkt.eth.dst]
    else:
        return STP[in_port]