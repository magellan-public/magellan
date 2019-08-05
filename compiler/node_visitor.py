import ast
import astunparse
from compiler.variable import Variable
from compiler.instruction import Instruction

class NodeVisitor(ast.NodeVisitor):
    def __init__(self, fp):
        self.fp = fp

        # check whether in on_packet
        self.context = None
        self.guardStack = [None]

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Dict):
            variable = self.fp.get_variable(node.targets[0].id, True)
            variable.type = 'map'
            if variable.value is None:
                variable.value = {}
            if self.context is None:
                variable.isGlobal = True
            self.fp.add_variable(variable)

        if isinstance(node.targets[0], ast.Subscript): # assign to map
            gv = self.fp.new_guard_variable()
            inst = Instruction(self.guardStack[-1], [self.visit(node.value), self.visit(node.targets[0])],
                               [gv], 'neq')
            self.fp.add_instruction(inst)
            self.guardStack.append(gv)

            var = self.fp.new_variable()
            inst = Instruction(self.guardStack[-1], [self.fp.get_variable(node.targets[0].value.id), self.visit(node.targets[0].slice.value)], [var], 'varof')
            self.fp.add_instruction(inst)
            inst = Instruction(self.guardStack[-1], [self.fp.get_variable(node.value.id)], [var], 'assign')
            self.fp.add_instruction(inst)
            self.guardStack.pop()


    def visit_Attribute(self, node):
        return Variable(astunparse.unparse(node).strip())

    def visit_FunctionDef(self, node):
        if node.name == 'on_packet':
            self.context = 'on_packet'
            for arg in node.args.args:
                variable = Variable(arg.arg)
                self.fp.add_variable(variable)
            self.generic_visit(node)

    def visit_If(self, node):
        gv = self.fp.new_guard_variable()
        mapping = self.get_mapping(node.test.ops[0])
        inst = Instruction(self.guardStack[-1], [self.visit(node.test.left), self.visit(node.test.comparators[0])],
                           [gv], mapping)
        self.fp.add_instruction(inst)
        self.guardStack.append(gv)
        self.visit(node.body[0])
        o = self.guardStack.pop()

        elsegv = self.fp.new_guard_variable()
        inst = Instruction(self.guardStack[-1], [o], [elsegv], 'not')
        self.fp.add_instruction(inst)
        self.guardStack.append(elsegv)
        self.visit(node.orelse[0])
        self.guardStack.pop()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            return self.fp.get_variable(node.id)
        else:
            return self.fp.new_variable(node.id)

    def visit_Subscript(self, node):
        var = self.fp.new_variable()
        inst = Instruction(self.guardStack[-1],
                           [self.fp.get_variable(node.value.id), self.visit(node.slice.value)],
                           [var], 'varof')
        self.fp.add_instruction(inst)
        return var

    def visit_Return(self, node):
        ret_val = self.fp.get_variable('return')
        if ret_val is None:
            ret_val = self.fp.new_variable('return')

        if isinstance(node.value, ast.Subscript):
            inst = Instruction(self.guardStack[-1], [self.fp.get_variable(node.value.value.id), self.visit(node.value.slice.value)], [ret_val], 'varof')
        else:
            inst = Instruction(self.guardStack[-1], [self.visit(node.value)], [ret_val], 'assign')
        self.fp.add_instruction(inst)


    def get_mapping(self, ops):
        if isinstance(ops, ast.Eq):
            return 'eq'
        elif isinstance(ops, ast.In):
            return 'in'
        elif isinstance(ops, ast.Add):
            return 'add'
        else:
            return 'nop'