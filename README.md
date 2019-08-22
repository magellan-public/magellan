# Magellan Compiler

# Overview
This compiler has 2 functions:
1. Translate high-level network-wide SDN program to P4 programs for each device
2. Generate runtime program on Controller


### System requirements
* You need a Linux OS to run the compiler and demo apps, typically Ubuntu Server 16.04 is preferred
* Make sure you have `python3` and `python3-pip` installed

## Get Started
Here we get started by compiling and running the L2 network which supports Mac learning and STP
### Step1: Prepare for the mininet(BMv2) environment
please refer to the link
https://github.com/p4lang/behavioral-model

### Step2: Clone the code to a directory
```commandline
# git clone --depth=1 https://github.com/magellan-public/magellan.git
# cd magellan
```
### Step3: Install the dependencies
```commandline
# pip install -r requirements.txt
```
### Step4: Compile the L2 magellan application
```commandline
# magc -a test/apps/l2 -t test/apps/l2.json -o build
```
### Step5: Start mininet(BMv2) environment

### Step6: Ping from h1 to h2
In mininet CLI, emit the following command to test connectivity


```sh
# start Mininet-P4 and make sure the container ip is 172.17.0.2
sudo docker run -it --rm --privileged dennisyu/mnp4
cd /root
./start.sh

# start Magellan controller
sudo docker run -it --rm dennisyu/magctl
cd /root
./test.sh

# test in Mininet
h1 ping h2

```

