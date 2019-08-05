class Variable:
    def __init__(self, name):
        self.name = name
        self.value = None
        self.type = None
        self.isGlobal = False
        self.ssa = []
        self.ssa_id = 0
        self.aliases = []

    def dump(self):
        if self.type == 'int':
            return '%s(%s)' % (self.name, str(self.values[0]))
        elif self.type == 'str':
            return '%s(\'%s\')' % (self.name, str(self.values[0]))
        else:
            return self.name

class RefVariable(Variable):
    def __init__(self, name, dst):
        super(RefVariable, self).__init__(name, 'ref')
        self.dst = dst