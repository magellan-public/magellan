class Schema:
    def __init__(self):
        self.inputs = []
        self.outputs = []


class Table:
    def __init__(self):
        self.schema = Schema()
        self.entries = []
