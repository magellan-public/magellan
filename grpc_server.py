from magellan.magellan_pb2 import *
from magellan.magellan_pb2_grpc import *
from concurrent import futures
import time, json
from compiler.compiler import compile

_HOST = 'localhost'
_PORT = '7777'

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

variables = {}


class gRPCServicerImpl(gRPCServicer):

    def SetVariable(self, request, context):
        print ("called with " + request.name)
        variables[request.name] = json.loads(request.value)
        compile('apps/l3/on_packet.py', variables)
        return Response()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_gRPCServicer_to_server(gRPCServicerImpl(), server)
    server.add_insecure_port('[::]:' + _PORT)
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
