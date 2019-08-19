# Magellan Compiler

# Overview
This compiler has 2 functions:
1. Translate high-level network-wide SDN program to P4 programs for each device
2. Generate runtime program on Controller

## Try first
```sh
# start Mininet-P4 and make sure the container ip is 172.17.0.2
sudo docker run -it --rm --privileged dennisyu/mnp4
cd /root
./start.sh

# start Magellan controller


# test in Mininet
h1 ping h2

```

## Directories
* compiler - the core compiler
* deployer - convert global PIT to per-switch Pipeline
* adapter  - convert per-switch Pipeline to device configuration
* proto   - not used
* resource - resource file
* utils    - utility
* test
    * apps - use cases
    * topology - test topology 

## Compiler Process
1. Takes in an application directory as compiler source
2. For each `on_packet` function, translate it to a set of flow-programs
3. For each flow-program, generate PIT pipeline (schema)
4. Run offline program to initialize variables and generate PIT entries
5. For each flow-program, project the PITs to each device on the `PATH` which the last PIT returns

## Coding Notes
* Use python3 interpreter so that we support python 3 annotation grammar

## Architecture
![Image text](https://raw.githubusercontent.com/guodong/magellan-pcl/master/docs/arch.png)

## Workflows
![Image text](https://raw.githubusercontent.com/guodong/magellan-pcl/master/docs/workflow.png)