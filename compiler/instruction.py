from compiler.table import Table
from compiler.variable import RefVariable,ConstantVariable,TupleVariable
NONSENSE="None"
MATCHANY="*"
PRIORITY="pri"
DATA="data"
TRUE="True"
FALSE="False"

class Instruction:
    def __init__(self, gv, inputs, outputs, mapping):
        self.gv = gv
        self.inputs = inputs
        self.outputs = outputs
        self.mapping = mapping
        self.pit = Table()
    def gen_pit(self):

        for output in self.outputs:
            self.pit.schema.outputs.append(output.name)

        if self.gv is not None:
            self.pit.schema.inputs.append(self.gv.name)

        if self.mapping == 'varof':
            self.pit.schema.inputs.append(self.inputs[1].name)
            self.outputs[0].value=[]
            for (k, v) in self.inputs[0].value.items():
                entry = { PRIORITY:1,
                DATA:{
                    self.inputs[1].name: k,
                    self.outputs[0].name: v}
                }
                if self.gv is not None:
                    entry[DATA].update({self.gv.name:TRUE})
                self.pit.entries.append(entry)
                self.outputs[0].value.append(v)
            entry1 = { PRIORITY:1,
                DATA:{
                    self.inputs[1].name: MATCHANY,
                    self.outputs[0].name: NONSENSE}
            }
            if self.gv is not None:
                entry1[DATA].update({self.gv.name:FALSE})
            self.pit.entries.append(entry1)
            entry2 = { PRIORITY:0,
                DATA:{
                    self.inputs[1].name: MATCHANY,
                    self.outputs[0].name: NONSENSE}
            }
            if self.gv is not None:
                entry2[DATA].update({self.gv.name:TRUE})
            self.pit.entries.append(entry2)
        elif self.mapping == 'in':
            self.pit.schema.inputs.append(self.inputs[0].name)
            v = self.inputs[1]
            if isinstance(self.inputs[1], RefVariable):
                v = self.inputs[1].dst
            for val in v.value.keys():
                entry = {
                    PRIORITY:1,
                    DATA:{
                    self.inputs[0].name: val,
                    self.outputs[0].name: TRUE
                    }
                }
                if self.gv is not None:
                    entry[DATA].update({self.gv.name:TRUE})
                self.pit.entries.append(entry)
            entry = {
                    PRIORITY:0,
                    DATA:{
                    self.inputs[0].name: MATCHANY,
                    self.outputs[0].name: FALSE
                    }
            }
            if self.gv is not None:
                entry[DATA].update({self.gv.name:FALSE})
            self.pit.entries.append(entry)
        elif self.mapping == 'neq' or self.mapping == 'eq':
            if self.mapping == 'neq':
                Ebiao=FALSE
                NEbiao=TRUE
            else:
                Ebiao=TRUE
                NEbiao=FALSE
            for input in self.inputs:
                self.pit.schema.inputs.append(input.name)
            if isinstance(self.inputs[0],ConstantVariable):
                self.pit.schema.inputs.remove(self.inputs[0].name)
                Biao=0
            elif isinstance(self.inputs[1],ConstantVariable):
                self.pit.schema.inputs.remove(self.inputs[1].name)
                Biao=1
            elif (len(self.inputs[0].value)<len(self.inputs[1].value)):
                Biao=0
            else:
                Biao=1
            for ev in self.inputs[Biao].value:
                if isinstance(self.inputs[Biao],ConstantVariable):
                    entry = {
                    PRIORITY:1,
                    DATA:{
                    self.inputs[(1-Biao)].name: ev,
                    self.outputs[0].name: Ebiao}
                    }
                else:
                    entry = {
                        PRIORITY:1,
                        DATA:{
                        self.inputs[0].name: ev,
                        self.inputs[1].name: ev,
                        self.outputs[0].name: Ebiao}
                    }
                if self.gv is not None:
                    entry[DATA].update({self.gv.name:TRUE})
                self.pit.entries.append(entry)
            if isinstance(self.inputs[Biao],ConstantVariable):
                entryD = {
                    PRIORITY:0,
                    DATA:{
                    self.inputs[(1-Biao)].name: MATCHANY,
                    self.outputs[0].name: NEbiao}
                    }
            else:
                entryD = {
                    PRIORITY:0,
                    DATA:{
                    self.inputs[0].name: MATCHANY,
                    self.inputs[1].name: MATCHANY,
                    self.outputs[0].name: NEbiao}
                }

            if self.gv is not None:
                entryD[DATA].update({self.gv.name:TRUE})
            self.pit.entries.append(entryD)
        elif self.mapping == 'assign' :  #input can't be map
            if  self.outputs[0].name == "return":
                self.pit=None
            else:
                for input in self.inputs:
                    self.pit.schema.inputs.append(input.name)  
                for i in self.inputs[0].value:
                    entry = {
                    PRIORITY:1,
                    DATA :{
                        self.inputs[0].name: i,
                        self.outputs[0].name: i
                        }
                    }
                    if self.gv is not None:
                        entry[DATA].update({self.gv.name:TRUE})
                    self.pit.entries.append(entry)
        elif self.mapping == 'shortestPath':
            for input in self.inputs:
                self.pit.schema.inputs.append(input.name)
            for i in self.inputs[0].value:
                for j in self.inputs[1].value:
                    entry = {
                    PRIORITY:1,
                    DATA :{
                        self.inputs[0].name: i,
                        self.inputs[1].name: j,
                        self.outputs[0].name: "shortestPath("+i+","+j+")"
                        }
                    }
                    self.outputs[0].value.append( "shortestPath("+i+","+j+")")
                    if self.gv is not None:
                        entry[DATA].update({self.gv.name:TRUE})
                    self.pit.entries.append(entry)
        elif self.mapping == 'spanningTree' : 
            for input in self.inputs:
                self.pit.schema.inputs.append(input.name)

            for i in self.inputs[0].value:
                entry = {
                PRIORITY:1,
                DATA :{
                    self.inputs[0].name: i,
                    self.outputs[0].name: "spanningTree("+i+")"
                    }
                }
                self.outputs[0].value.append( "spanningTree("+i+")")
                if self.gv is not None:
                    entry[DATA].update({self.gv.name:TRUE})
                self.pit.entries.append(entry)
        elif self.mapping == 'not':
            for input in self.inputs:
                self.pit.schema.inputs.append(input.name)

            self.pit.entries.append({
                PRIORITY:1,
                DATA:{
                self.gv.name:TRUE,
                self.inputs[0].name: TRUE,
                self.outputs[0].name: FALSE}
            })
            self.pit.entries.append({
                PRIORITY:1,
                DATA:{
                self.gv.name:TRUE,
                self.inputs[0].name: FALSE,
                self.outputs[0].name: TRUE}
            })
        elif self.mapping == 'toController':
            for input in self.inputs:
                self.pit.schema.inputs.append(input.name)

            self.pit.entries.append({
                PRIORITY:1,
                DATA:{
                self.gv.name:TRUE,
                self.inputs[0].name: MATCHANY,
                self.inputs[1].name: MATCHANY,
                self.outputs[0].name: "toController"}
            })
            self.pit.entries.append({
                PRIORITY:0,
                DATA:{
                self.gv.name:TRUE,
                self.inputs[0].name: MATCHANY,
                self.inputs[1].name: MATCHANY,
                self.outputs[0].name: NONSENSE}
            })
            
        else:
            for input in self.inputs:
                self.pit.schema.inputs.append(input.name)

    '''

    def gen_pit(self):

        for output in self.outputs:
            self.pit.schema.outputs.append(output.name)

        if self.gv is not None:
            self.pit.schema.inputs.append(self.gv.name)

        if self.mapping == 'varof':
            self.pit.schema.inputs.append(self.inputs[1].name)
            for (k, v) in self.inputs[0].value.items():
                entry = {
                    self.inputs[1].name: k,
                    self.outputs[0].name: v
                }
                if self.gv is not None:
                    entry[self.gv.name] = 'True'
                self.pit.entries.append(entry)
        elif self.mapping == 'in':
            self.pit.schema.inputs.append(self.inputs[0].name)
            v = self.inputs[1]
            if isinstance(self.inputs[1], RefVariable):
                v = self.inputs[1].dst
            for val in v.value.keys():
                entry = {
                    self.inputs[0].name: val,
                    self.outputs[0].name: 'True'
                }
                if self.gv is not None:
                    entry[self.gv.name] = 'True'
                self.pit.entries.append(entry)
        elif self.mapping == 'neq':
            for input in self.inputs:
                self.pit.schema.inputs.append(input.name)
            for i in range(1, 16):
                entry = {
                    self.inputs[0].name: str(i),
                    self.inputs[1].name: str(i),
                    self.outputs[0].name: 'False',
                }
                if self.gv is not None:
                    entry[self.gv.name] = 'True'
                self.pit.entries.append(entry)
        elif self.mapping == 'assign':
            for input in self.inputs:
                self.pit.schema.inputs.append(input.name)

            for i in range(1, 16):
                entry = {
                    self.inputs[0].name: str(i),
                    self.outputs[0].name: str(i),
                }
                if self.gv is not None:
                    entry[self.gv.name] = 'True'
                self.pit.entries.append(entry)
        elif self.mapping == 'not':
            for input in self.inputs:
                self.pit.schema.inputs.append(input.name)

            self.pit.entries.append({
                self.inputs[0].name: 'True',
                self.outputs[0].name: 'False',
            })
            self.pit.entries.append({
                self.inputs[0].name: 'False',
                self.outputs[0].name: 'True',
            })
        else:
            for input in self.inputs:
                self.pit.schema.inputs.append(input.name)
'''


    def dump(self):
        if self.gv is not None:
            if len(self.outputs) == 0:
                print('if %s: %s(%s)' % (self.gv.name, self.mapping,
                                          ', '.join(map(lambda s: s.dump(), self.inputs))))
            else:
                print('if %s: %s = %s(%s)' % (self.gv.name, ', '.join(map(lambda s: s.dump(), self.outputs)), self.mapping,
                                          ', '.join(map(lambda s: s.dump(), self.inputs))))
        else:
            if len(self.outputs) == 0:
                print('%s(%s)' % (self.mapping,
                                       ', '.join(map(lambda s: s.dump(), self.inputs))))
            else:
                print('%s = %s(%s)' % (', '.join(map(lambda s: s.dump(), self.outputs)), self.mapping,
                                   ', '.join(map(lambda s: s.dump(), self.inputs))))
        # s1 = ' '.join(map(lambda s: astunparse.unparse(s), self.outputs))
        # print '%s = func(%s)' % (s1, ' '.join(map(lambda s: astunparse.unparse(s), self.inputs)))
        # print '%s = assign(%s)' % (' '.join(map(lambda s: s.id, self.outputs)), ' '.join(map(lambda s: s.n, self.inputs)))

    def dump_pit(self):
        # if self.mapping == 'valof':

        # gv = ''
        # if self.gv is not None:
        #     gv = self.gv.name
        #     print '%s | %s -> %s' % (gv, '|'.join(self.pit.schema.inputs), '|'.join(self.pit.schema.outputs))
        # else:
        if not(self.pit is None):
            print (PRIORITY,end='|')
            print ('%s -> %s' % ('|'.join(self.pit.schema.inputs), '|'.join(self.pit.schema.outputs)))
            for entry in self.pit.entries:
                print (entry[PRIORITY] ,end='|')
                for input_name in self.pit.schema.inputs:
                    print (entry[DATA][input_name], end= '|')
                for output_name in self.pit.schema.outputs:
                    print (entry[DATA][output_name])

    '''
    def dump_pit(self):
        # if self.mapping == 'valof':

        # gv = ''
        # if self.gv is not None:
        #     gv = self.gv.name
        #     print '%s | %s -> %s' % (gv, '|'.join(self.pit.schema.inputs), '|'.join(self.pit.schema.outputs))
        # else:
        print('%s -> %s' % ('|'.join(self.pit.schema.inputs), '|'.join(self.pit.schema.outputs)))


        for entry in self.pit.entries:
            for input_name in self.pit.schema.inputs:
                print(entry[input_name] + '|',)
            for output_name in self.pit.schema.outputs:
                if isinstance(entry[output_name], list):
                    print(entry[output_name])
                else:
                    print(entry[output_name])
    '''

    