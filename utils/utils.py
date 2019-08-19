
def error(*msg):
    print(*msg)
    exit(-1)


def parse_mac(s):
    assert isinstance(s, str)
    return (int(s.replace(':',''),16), 0xffffffffffff, 48)
