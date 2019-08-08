# Magellan Compiler

# Overview
This compiler has 2 functions:
1. Translate high-level network-wide SDN program to P4 programs for each device
2. Generate runtime program on Controller

## Directories
* apps - The use cases 
* compiler - The core compiler
* magellan - The library for writing offline program
* out - The generated P4 files and runtime program

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