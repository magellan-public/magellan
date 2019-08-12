import os

from compiler import compile
from deployer.generator import FlowRulesGenerator
from deployer.datastore_proxy import DatastoreProxy
from adapter.openflow import OpenFlowAdapter
from adapter.p4 import P4Adapter

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.abspath(__file__))
    app_dir = dir_path + '/test/apps/l2/'
    dp_file = app_dir + 'on_packet.mag'
    offline_file = app_dir + 'offline.py'
    ds_file = app_dir + 'ds.json'
    topo_file = dir_path + '/test/topology/l2.json'
    template_file = dir_path + '/resource/p4_tag.tpl'
    result_dir = 'out/'
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

    # of_adp = OpenFlowAdapter()
    # of_adp.update(fg.get_per_switch_config())
    p4_adp = P4Adapter(template_file, result_dir = result_dir)
    p4_adp.update(fg.get_per_switch_config())


