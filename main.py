# from grpc_server import serve
from compiler import compile
from deployer.pit2dataplane import *

if __name__ == '__main__':

    #app_dir = 'D:/CZU/PengCheng/magellan-pcl/apps/l2'
    app_dir = 'apps/l2'
    dp_file = app_dir + '/on_packet.mag'
    offline_file = app_dir + '/offline.py'
    out_dir = 'out'
    portTag, pipeline = compile(dp_file, None)

    for table in pipeline:
        print("inputs: " + str(table.schema.inputs))
        print("outputs: " + str(table.schema.outputs))
        print(str(table.entries))

    ds = DatastoreProxy('topologies/l2.json')
    fg = FlowRulesGenerator(ds)

    fg.accept_new_pit(portTag, pipeline)
    fg.dump()

    
    # t = Thread(target=serve, args=(fp)).start()
    # serve()


