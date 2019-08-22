import ast
import json
import os
from time import sleep

# from adapter.openflow import OpenFlowAdapter
from adapter.p4 import P4Adapter
from compiler import compile
from compiler.flow_program import FlowProgram
from compiler.node_visitor import NodeVisitor
from deployer.datastore_proxy import DatastoreProxy
from deployer.generator import FlowRulesGenerator


class Compiler:
    def __init__(self, source_file, topo_file, result_dir="/tmp/"):
        self._topo_file = topo_file
        self._source_file = source_file
        self._ast_root = None
        self._result_dir = result_dir
        dir_path = os.path.dirname(os.path.abspath(__file__))
        self._template_file = dir_path + '/resource/p4_tag.tpl'

    def compile_ast(self, verbose=False):
        if verbose:
            sleep(0.3)
            print("compile %s"%str(self._source_file))
        with open(self._source_file, 'r') as f:
            self._ast_root = ast.parse(f.read())

    def compile_result(self, variables, verbose=False):
        fp = FlowProgram(variables)
        if verbose:
            import pickle
            with open(self._result_dir+"ds.pickle", "wb") as f:
                f.write(pickle.dumps(fp))

        visitor = NodeVisitor(fp)
        visitor.visit(self._ast_root)
        # fp.dump()
        if verbose:
            sleep(0.3)
            print("generate flow program")
            with open(self._result_dir+"flowprogram.txt", "w") as f:
                f.write(fp.dump_str())

        fp.gen_pit_pipeline()
        # fp.dump_pit()
        if verbose:
            sleep(0.3)
            print("generate pit")
            with open(self._result_dir+"pit.txt", "w") as f:
                f.write(fp.dump_pit_str())

        portTag, pipeline = fp.ret_pit_pipeline()
        ds = DatastoreProxy(self._topo_file)
        fg = FlowRulesGenerator(ds)
        fg.accept_new_pit(portTag, pipeline)
        # fg.dump()
        if verbose:
            sleep(0.3)
            print("generate datapath")
            with open(self._result_dir+"datapath.txt", "w") as f:
                f.write(fg.dump_str())

        p4_adp = P4Adapter(self._template_file, result_dir=self._result_dir)
        p4_adp.update(fg.get_per_switch_config())


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.abspath(__file__))
    app_dir = dir_path + '/test/apps/l2/'
    dp_file = app_dir + 'on_packet.mag'
    # offline_file = app_dir + 'offline.py'
    ds_file = app_dir + 'ds.json'
    topo_file = dir_path + '/test/topology/l2-p4.json'
    template_file = dir_path + '/resource/p4_tag.tpl'
    result_dir = '/home/yutao/Work/p4/tutorials/magellan-testbed/pipe/'
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


