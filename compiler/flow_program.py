from compiler.variable import Variable, ConstantVariable, TupleVariable


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

    def new_constant_variable(self, value):
        name = self.__gen_variable_name()
        var = ConstantVariable(name, value)
        self.variables.append(var)
        return var

    def new_tuple_variable(self, elts):
        name = self.__gen_variable_name()
        var = TupleVariable(name, elts)
        self.variables.append(var)
        return var

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
        self.get_variable("inport").value.extend(["s1:1","s5:1"])
        #self.get_variable("global_mac_table").value={"00:00:00:00:00:02":"s1:1","00:00:00:00:00:01":"s5:1"}
        for inst in self.instructions:
            inst.gen_pit()

    def ret_pit_pipeline(self):
        retlist=[]
        for inst in self.instructions:
            if not(inst.pit is None):
                retlist.append(inst.pit)
        return self.get_variable('__v1').value[0],retlist   #port_label, list(pit_table)

    def dump(self):
        print('++++++ flow program ++++++')
        for inst in self.instructions:
            inst.dump()

    def dump_pit(self):
        print('++++++ pit pipeline ++++++')
        for inst in self.instructions:
            inst.dump_pit()
            print('')

    # def gen_p4(self):
    #     tables = []
    #     for (idx, inst) in enumerate(self.instructions):
    #         table = {
    #             'name': 't' + str(idx+1),
    #             'matches': inst.pit.schema.inputs,
    #             'actions': inst.pit.schema.outputs[0]
    #         }
    #         tables.append(table)
    #
    #     with open('p4.tpl') as f:
    #         template = Template(f.read())
    #         print(template.render(tables=tables))