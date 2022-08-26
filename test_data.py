import json

with open('ref-valid.jsonl', 'r') as f:
    count = 0
    for line in f.readlines():
        jd = json.loads(line)
        for k, v in jd.items():
            if k == 'old' or k == 'new':
                print(f'{k} : {v}')
            count += 1
        if count >= 100:
            break