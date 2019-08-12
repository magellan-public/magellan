
class host:
    id=-1
    switchid=-1
    address=-1
    def __init__(self,i,s,a):
        self.id=i
        self.switchid=s
        self.address=a

class link:
    id=-1
    leftnode=-1
    rightnode=-1
    weight=1;
    def __init__(self,l,r):
        #self.id=i
        self.leftnode=l
        self.rightnode=r
    def set_weight(w):
        self.weight=w;

class port:
    
    def __init__(self,n,d): 
        self.nodeid=n
        self.dstid=d
        #self.plink=l
    def set_id(self,i):
        self.id=i
class node:
     def __init__(self,i):
         self.id=i
         self.portlist=[]
         self.floodportset=set()
         self.portnum=0
     def add_port(self,port):
        self.portlist.append(port)
      



