from .value_type import *

class Pipeline:
    def __init__(self, pit):
        self.pipelineTables = []

        self.initialize(pit)

    def initialize(self, pit):

        nameTable = self.computeNameTable(pit)
        nameValueTable = self.computeNameValueTable(pit)

        table_id = 0

        for table in pit:
            pipelineTable = PipelineTable(table_id, table, nameTable, nameValueTable)
            self.pipelineTables.append(pipelineTable)
            table_id += 1

    # nameTable: '__v6': 'r9'
    def computeNameTable(self, pit):
        nameTable = {}
        regCount = 0
        for table in pit:
            schema = table.schema

            inputs = schema.inputs
            outputs = schema.outputs

            for input in inputs:
                if 'pkt' in input:
                    nameTable[input] = input
                else:
                    if input not in nameTable:
                        nameTable[input] = 'r' + str(regCount)
                        regCount += 1

            for output in outputs:
                if 'pkt' in output:
                    nameTable[output] = output
                else:
                    if output not in nameTable:
                        nameTable[output] = 'r' + str(regCount)
                        regCount += 1
        return nameTable

    # nameValueTable: '__v6': {'s1:1': '10'}
    def computeNameValueTable(self, pit):
        nameValueTable = {}

        for table in pit:
            entries = table.entries
            for entry in entries:
                kvs = entry['data']
                for key in kvs:
                    print(key)
                    value = kvs[key]
                    print(value)
                    if get_type(value) == MAC or get_type(value) == IPv4 or get_type(value) == ANY\
                            or get_type(value) == SP or get_type(value) == STP or get_type(value) == DROP\
                            or get_type(value) == PUNT:
                        continue
                    else:
                        if key in nameValueTable:
                            valueTable = nameValueTable[key]
                            if value not in valueTable:
                                count = len(valueTable)
                                valueTable[value] = count
                        else:
                            valueTable = {}
                            valueTable[value] = 0
                            nameValueTable[key] = valueTable

        return nameValueTable

    def dump(self):
        for pipelineTable in self.pipelineTables:
            pipelineTable.dump()





class PipelineTable:
    def __init__(self, id, table, nameTable, nameValueTable):
        self.tableId = id
        self.flowRules = []

        self.initialize(table, nameTable, nameValueTable)

    def initialize(self, table, nameTable, nameValueTable):
        schema = table.schema
        entries = table.entries

        inputs = schema.inputs
        outputs = schema.outputs

        for entry in entries:
            flowRule = FlowRule(entry, inputs, outputs, nameTable, nameValueTable)
            self.flowRules.append(flowRule)

    def dump(self):
        print("table id: " + str(self.tableId))
        for flowrule in self.flowRules:
            flowrule.dump()


class FlowRule:
    '''
    entry, inputs, and outputs are defined in table.py
    nameTable is specified in Pipeline that has variable in instruction to metadata (register) in dataplane, e.g., '__v6' -> 'r1'
    nameValueTable is specified in Pipeline that has name to valueTable, e.g., 'port' -> 's1:1' -> '2'
    '''
    def __init__(self, entry, inputs, outputs, nameTable, nameValueTable):

        self.priority = entry['pri']
        self.matches = {}
        self.actions = []

        self.initialize(entry, inputs, outputs, nameTable, nameValueTable)

    '''
    guardvariable value: True False, *
    port value: s1:1, h1:2, *
    packet header value: 00:00:00:00:00:00, 10.0.0.1, *
    function value: shortestPath('s1:1', 'h2:1') spanningTree('s1:1') DROP() toController()
    none value: None
    '''
    def initialize(self, entry, inputs, outputs, nameTable, nameValueTable):
        kvs = entry['data']
        for key in kvs:
            value = kvs[key]
            if key in inputs:
                type = get_type(value)
                if type == MAC or type == IPv4 or type == ANY:
                    self.matches[nameTable[key]] = value
                else:
                    self.matches[nameTable[key]] = nameValueTable[key][value]
            else:
                type = get_type(value)
                if type == SP or type == STP or type == PUNT or type == DROP:
                    action = GlobalAction(TERMINAL_ACTION, value, None, None)
                    self.actions.append(action)
                else:
                    action = GlobalAction(NON_TERMINAL_ACTION, None, nameTable[key], nameValueTable[key][value])
                    self.actions.append(action)

    def dump(self):
        print('pri:' + str(self.priority) + ' | matches:' + str(self.matches) + " | actions:" + str(self.actions))


TERMINAL_ACTION = 0
NON_TERMINAL_ACTION = 1


class GlobalAction:
    def __init__(self, type, action, key, value):
        self.type = type
        self.action = action  # is valid only type is TERMINAL_ACTION
        self.key = key
        self.value = value

    def __repr__(self):
        if self.type == NON_TERMINAL_ACTION:
            return "set " + str(self.key) + " to " + str(self.value)
        else:
            return self.action


if __name__ == '__main__':
    type = get_type('None')
    print(type)





