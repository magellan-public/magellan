import json
from magellan_pb2 import *
from magellan_pb2_grpc import *


def set(varname, value):
    conn = grpc.insecure_channel('localhost:7777')
    client = gRPCStub(channel=conn)
    client.SetVariable(Variable(name=varname, value=json.dumps(value)))


def get(varname):
    pass

def new_packet(type, args):
    pass

def send_packet(pkt, port):
    pass