import re

GV = 0
PORT = 1
MAC = 2
IPv4 = 3
SP = 4
STP = 5
DROP = 6
PUNT = 7
Null = 8
ANY = 9

def is_special_code_by_key(key):
    if key == 'inport_label' or key == 'inport':
        return True
    return False

def get_type(value):
    if value == 'True' or value == 'False':
        return GV
    elif 'shortestPath' in value:
        return SP
    elif 'spanningTree' in value:
        return STP
    elif 'DROP' in value:
        return DROP
    elif 'toController' in value:
        return PUNT
    elif re.match("s|h[0-9]+\:[0-9]+", value):
        return PORT
    elif re.match("(?:[0-9a-fA-F]:?){12}", value):
        return MAC
    elif re.match("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", value):
        return IPv4
    elif value == 'None':
        return Null
    elif value == '*':
        return ANY
