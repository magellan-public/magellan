import ast
import astunparse
from compiler.flow_program import FlowProgram
from compiler.node_visitor import NodeVisitor


def compile(file, variables):
    fp = FlowProgram(variables)
    visitor = NodeVisitor(fp)
    with open(file, 'r') as f:
        root = ast.parse(f.read())
        print(astunparse.dump(root))
        visitor.visit(root)

        # fp.dump()
        # fp.gen_pit_pipeline()
        # fp.dump_pit()
        # fp.gen_p4()