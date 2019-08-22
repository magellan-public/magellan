# Magellan Compiler

## Overview
This compiler has 2 functions:
1. Translate high-level network-wide SDN program to P4 programs for each device
2. Generate runtime program on Controller

## Get Started
Here we get started by compiling and running the L2 network which supports Mac learning and STP,
the program is as follows

```python
from topology import shortestPath, spanningTree

global_mac_table = {} # mac -> the 'h->e' port ('00:00...' -> 's1:1')

def on_packet(pkt, inport: 'external_ingress'):
  global_mac_table.insert(pkt.eth.src, inport, 500) # key, value, timeout

  if pkt.eth.dst in global_mac_table:
    return shortestPath(inport, global_mac_table[pkt.eth.dst]), pkt
  else:
    return spanningTree(inport), pkt
```


### System requirements
* You need a Linux OS to run the compiler and demo apps, typically Ubuntu Server 16.04 is preferred
* Make sure you have `python3` and `python3-pip` installed

### Steps

#### Step1: Prepare for the mininet(BMv2) environment
please install [bmv2](https://github.com/p4lang/behavioral-model) and [mininet](https://github.com/mininet/mininet),
and follow the [p4 tutorial](https://github.com/p4lang/tutorials) to get some [helper script](https://github.com/p4lang/tutorials/blob/master/utils/run_exercise.py). 

#### Step2: Clone the code to a directory
```commandline
# git clone --depth=1 https://github.com/magellan-public/magellan.git
```

#### Step3: Install the dependencies and setup
```commandline
# pip install -r requirements.txt
# python3 setup.py
```

#### Step4: Start mininet(BMv2) environment and ping from h1 to h2
start a mininet with 4 switches and 2 hosts, and ping from h1 to h2, at this moment, the ping command will fail.
```commandline
# python run_exercise.py -t test/topology/l2-mn.json -b simple_switch_grpc
# h1 ping h2
```

#### Step5: Compile the L2 magellan application
compile the l2 test application to a directory, this step will generate initial p4 pipeline source code and runtime flow rules.
```commandline
# magc -a test/apps/l2/on_packet.mag -t test/topology/l2-p4-4sw.json -o build
```

#### Step6: Run the program
start the l2 program as follows, then the ping command will success.
```commandline
# mag_run -d build
```

