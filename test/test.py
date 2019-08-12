from jinja2 import Template


def p4_render():
    variables = [
        {
            "len": 1,
            "name": "reg1"
        }
    ]

    tables = [
        {
            "name": "table1",
            "action_parm_str": "bit<1> v0, bit<2> v1",
            "action_str": "meta.reg0=v0;meta.reg1=v1;",
            "matches": [
                {
                    "name" : "hdr.ethernet.src",
                    "type" : "ternary"
                },
                {
                    "name": "meta.reg1",
                    "type" : "exact"
                }
            ],
            "size" : 65536
        },
        {
            "name": "tag_table",
            "action_parm_str": "bit<1> v0, bit<2> v1",
            "action_str": "meta.reg0=v0;meta.reg1=v1;",
            "matches": [
                {
                    "name": "hdr.ethernet.src",
                    "type": "ternary"
                },
                {
                    "name": "meta.reg1",
                    "type": "exact"
                }
            ],
            "size": 65536
        }
    ]
    with open("../resource/p4_tag.tpl") as f:
        template = Template(f.read())
        print(template.render(tables=tables, variables=variables))


if __name__=="__main__":
    p4_render()