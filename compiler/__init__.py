import ast
import astunparse
import json
from compiler.flow_program import FlowProgram
from compiler.node_visitor import NodeVisitor


def compile(file, ds_file):
    with open(ds_file) as fp:
        variables = json.loads(fp.read())
        fp = FlowProgram(variables)
        visitor = NodeVisitor(fp)
        with open(file, 'r') as f:
            root = ast.parse(f.read())
            # print(astunparse.dump(root))
            visitor.visit(root)

            fp.dump()
            fp.gen_pit_pipeline()
            fp.dump_pit()
            return fp.ret_pit_pipeline()
            # fp.gen_p4()