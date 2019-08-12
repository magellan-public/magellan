from NetElement import node,link,port
import Store
import copy
def TR(switchid):
    return switchid-1

def init_linkTable():
    INFINITE=999
    Store.linkTable = [[INFINITE] * (len(Store.switches)) for _ in range(len(Store.switches))]
    for i in  Store.links:
        Store.linkTable[TR(i.leftnode)][TR(i.rightnode)]=i.weight
        Store.linkTable[TR(i.rightnode)][TR(i.leftnode)]=i.weight
    for i in range(len(Store.switches)):
        Store.linkTable[i][i]=0

def build_port():
    for i in  Store.links:
        p1=port(i.leftnode,i.rightnode)
        p2=port(i.rightnode,i.leftnode)
        Store.switches[TR(i.leftnode)].portnum+=1
        p1.set_id(Store.switches[TR(i.leftnode)].portnum)
        Store.switches[TR(i.leftnode)].add_port(p1)
        Store.switches[TR(i.rightnode)].portnum+=1
        p2.set_id(Store.switches[TR(i.rightnode)].portnum)
        Store.switches[TR(i.rightnode)].add_port(p2)
    for i in Store.hostlinks:
         p=port(i.leftnode,i.rightnode)
         Store.switches[TR(i.leftnode)].portnum+=1
         p.set_id(Store.switches[TR(i.leftnode)].portnum)
         Store.switches[TR(i.leftnode)].add_port(p)
'''
       for i in Store.switches:
       for p in i.portlist:
           print(str(p.nodeid)+" "+str(p.id))
'''

def init_STPTable():
     Store.STPTable = [[ [] for i in range(len(Store.switches))] for _ in range(len(Store.switches))]
     for i in  Store.links:
        p1=(i.leftnode,i.rightnode)
        p2=(i.rightnode,i.leftnode)
        Store.STPTable[TR(i.leftnode)][TR(i.rightnode)].append(p1)
        Store.STPTable[TR(i.rightnode)][TR(i.leftnode)].append(p2)
def get_topo():
   
    Store.switches=[node(1),node(2),node(3),node(4),node(5)]
    Store.links=[link(1,2),link(1,4),link(2,3),link(2,5),link(3,4),link(4,5)]
    Store.hostlinks=[link(1,"h1"),link(5,"h2")]


'''
def show_STPTable():
    for i in range(len(Store.switches)):
        for j in range(len(Store.switches)):
             for p in  Store.STPTable[i][j]:
                 if(p!=None):
                     print(str(i)+str(j)+"nodeid:"+str(p.nodeid)+" dstid:"+str(p.dstid))
   
'''  


def dijk(src):
    listpre=[src]
    listdst=[]
    INFINITE=999
    for j in  Store.switches:
        if(j.id!=src):
            listdst.append(j.id)
    linkLine=Store.linkTable[TR(src)]
    num=len(listdst)
    for d in range(num):
        minnode=listdst[0]
        mindistance=INFINITE
        for i in listdst:   
            if(Store.linkTable[TR(src)][TR(listpre[-1])]+Store.linkTable[TR(listpre[-1])][TR(i)]<linkLine[TR(i)]):
                linkLine[TR(i)]=Store.linkTable[TR(src)][TR(listpre[-1])]+Store.linkTable[TR(listpre[-1])][TR(i)]
                Store.STPTable[TR(src)][TR(i)][:] = []
                Store.STPTable[TR(src)][TR(i)].extend( Store.STPTable[TR(src)][TR(listpre[-1])])
                Store.STPTable[TR(src)][TR(i)].extend( Store.STPTable[TR(listpre[-1])][TR(i)])
 
            if(linkLine[TR(i)]<mindistance):
                minnode=i
                mindistance=linkLine[TR(i)]
        listpre.append(minnode)
        listdst.remove(minnode)

def dijkSTP():
    for t in Store.switches:
         dijk(t.id)

def get_portid(switch,dst):
    for p in Store.switches[TR(switch)].portlist:
        if(p.dstid==dst):
            return p.id

def build_perswitchFloodPortSet():
    Treeline=Store.STPTable[0]    
    for p in Treeline:
        for tup in p:
            Store.switches[TR(tup[0])].floodportset.add(get_portid(tup[0],tup[1]))
            Store.switches[TR(tup[1])].floodportset.add(get_portid(tup[1],tup[0]))

def get_networkstp():
    StpTreePortDict={}
    for s in Store.switches:      
        for p in s.portlist:
            spset=copy.deepcopy(s.floodportset)
            if(p.id in spset):
                spset.remove(p.id)
            if(s.id in  StpTreePortDict):
                 StpTreePortDict[s.id].update({p.id:list(spset)})
            else:
                StpTreePortDict.update({s.id:{p.id:list(spset)}} )   
        
    return StpTreePortDict
    
def for_Dong():
    get_topo()
    build_port()
    init_linkTable()
    init_STPTable()
    dijkSTP()
    build_perswitchFloodPortSet()
    return get_networkstp()

def main():
    '''
    get_topo()
    build_port()
    init_linkTable()
    init_STPTable()
    dijkSTP()
    build_perswitchFloodPortSet()
    print(Store.STPTable)
    #for s in Store.switches:
    #   print(s.floodportset)
    print(get_networkstp())
    '''
main()

