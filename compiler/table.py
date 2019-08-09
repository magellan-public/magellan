class Schema:
    def __init__(self):
        self.inputs = []
        self.outputs = []

'''

if g4: __v6 = shortestPath(inport, __v7)

self.inputs = ['g4', 'inport', '__v7']
self.outputs = ['__v6']

self.entries = [
    {'pri': 1, 'data': {'g4': 'True', 'inport': 's1:1', '__v7': 's2:2', '__v6': 'shortestPath("s1:1", "s2:2")'}},
    ...   
    {'pri': 0, 'data': {'g4': '*', ...., '__v6': 'None'}
]

gv: True|False
port: s1:1
mac: 11:11:11:11:11:11
function: shortestPath('s1:1', 'h2:1') spanningTree('s1:1') DROP() toController()
'''



class Table:
    def __init__(self):
        self.schema = Schema()
        self.entries = []

