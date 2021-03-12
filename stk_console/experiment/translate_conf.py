import pdb
import ConfigParser
import json
from collections import OrderedDict

jo = json.load(open('stk_console.v01.json'), object_pairs_hook=OrderedDict)
conf=ConfigParser.ConfigParser()
for key in jo.keys():
    conf.add_section(key)
    if not isinstance(jo[key],dict):
        continue
    for k,v in jo[key].items():
        conf.set(key,k,v)
conf.write(open('stk_console.v01.ini','w'))

# pdb.set_trace()
conf.read(open('stk_console.v01.ini'))
print conf.items('cn-ticks')
