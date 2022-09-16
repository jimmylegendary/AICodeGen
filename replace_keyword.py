import os
import json

orig_file="mydata.jsonl"
with open(orig_file,'r') as f:
    for line in f.readlines():
        data=json.loads(line)
        print(data['comment'])
        break
    f.close()
