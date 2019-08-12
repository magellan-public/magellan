# from grpc_server import serve
import os
from compiler import compile
from deployer.pit2dataplane import *
from adapter.openflow import OpenFlowAdapter

if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.abspath(__file__))
    app_dir = dir_path + '/test/apps/l2/'
    dp_file = app_dir + 'on_packet.mag'
    offline_file = app_dir + 'offline.py'
    ds_file = app_dir + 'ds.json'
    topo_file = dir_path + '/test/topology/l2.json'
    print(ds_file)
    # out_dir = 'out'
    portTag, pipeline = compile(dp_file, ds_file)

    '''
    for table in pipeline:
        print("inputs: " + str(table.schema.inputs))
        print("outputs: " + str(table.schema.outputs))
        print(str(table.entries))
    '''

    ds = DatastoreProxy(topo_file)
    fg = FlowRulesGenerator(ds)

    fg.accept_new_pit(portTag, pipeline)
    fg.dump()

    of_adp = OpenFlowAdapter()
    of_adp.update(fg.get_per_switch_config())
    
    # t = Thread(target=serve, args=(fp)).start()
    # serve()


