from compiler.variable import Variable
from jinja2 import Template

class FlowProgram:
    def __init__(self, variables=None):
        self.instructions = []
        self.variables = []
        self.__variableidx = 0

        if variables != None:
            for name, value in variables.items():
                var = self.new_variable(name)
                var.value = value
                self.variables.append(var)

    def __gen_variable_name(self, prifix='__v'):
        name = prifix + str(self.__variableidx)
        self.__variableidx += 1
        return name

    def add_variable(self, variable):
        self.variables.append(variable)

    def new_variable(self, name=None):
        if name is None:
            name = self.__gen_variable_name()
        variable = Variable(name)
        self.variables.append(variable)
        return variable

    def add_instruction(self, inst):
        self.instructions.append(inst)

    def get_variable(self, name, create=False):
        for var in self.variables:
            if var.name == name:
                if len(var.ssa) > 0:
                    return var.ssa[-1]
                else:
                    return var
            for alias in var.aliases:
                if alias == name:
                    if len(var.ssa) > 0:
                        return var.ssa[-1]
                    else:
                        return var

        if create:
            var = self.new_variable(name)
            return var
        else:
            return None

    def new_guard_variable(self):
        name = self.__gen_variable_name('g')
        variable = Variable(name)
        self.variables.append(variable)
        return variable

    def gen_pit_pipeline(self):
        for inst in self.instructions:
            inst.gen_pit()

    def dump(self):
        print('++++++ flow program ++++++')
        for inst in self.instructions:
            inst.dump()

    def dump_pit(self):
        print('++++++ pit pipeline ++++++')
        for inst in self.instructions:
            inst.dump_pit()
            print('')

    def gen_p4(self):
        tables = []
        for (idx, inst) in enumerate(self.instructions):
            table = {
                'name': 't' + str(idx+1),
                'matches': inst.pit.schema.inputs,
                'actions': inst.pit.schema.outputs[0]
            }
            tables.append(table)

        with open('p4.tpl') as f:
            template = Template(f.read())
            print(template.render(tables=tables))