class VlanTable:
    def __init__(self, port):
        self.port = port
        self.matches = {}

    def add_flow_rule(self, vlanId, outputs, isLast):
        self.matches[vlanId] = (outputs, isLast)

    def dump(self):
        print(self.matches)