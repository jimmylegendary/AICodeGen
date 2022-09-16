import os
import json

from util import RepoData

class CodeReviewDataManager:
    def __init__(self, path):
        self.data_list : list[CodeReviewData] = []
        self.root_path = path
        
    def save(self):
        data_dict : list[dict] = []
        for data in self.data_list:
            dd = dict()
            dd['old'] = data.old
            dd['new'] = data.new
            dd['comment'] = data.comment
            data_dict.append(dd)
            
        path = self.root_path + 'mydata.jsonl'
        with open(path , encoding= "utf-8",mode="w") as file: 
	        for i in data_dict: file.write(json.dumps(i) + "\n")

class CodeReviewData:
    def __init__(self, old='', new='', msg=''):
        self.old = old
        self.new = new
        self.comment = msg

data_manager = CodeReviewDataManager(path='./')

perf_keywords = [
            'perf',
            'optimize',
            'optimization',
            'time complexity'
        ]

def get_patch_dict(patch, msg):
    count = 0
    lines = [line for line in patch.split('\n')]
    lines = list(filter(len, lines))
    for idx in range(len(lines)):
        if lines[idx].startswith('@@'):
            count += 1
            old_patch_str = ''
            new_patch_str = ''
            while idx < len(lines) - 1:
                idx += 1
                if lines[idx].startswith('@@'):
                    idx -= 1
                    break
                lines[idx] = lines[idx] + '\n'
                if lines[idx][0] == '-':
                    old_patch_str += lines[idx]
                elif lines[idx][0] == '+':
                    new_patch_str += lines[idx]
                else:
                    old_patch_str += lines[idx]
                    new_patch_str += lines[idx]
        
            data_manager.data_list.append(CodeReviewData(
                old=old_patch_str, 
                new=new_patch_str,
                msg=msg
                )
            )

from types import SimpleNamespace
json_file = 'test.jsonl'
json_data = []
for line in open(json_file):
    try:
        json_data.append(json.loads(line, object_hook=lambda d:SimpleNamespace(**d)))
    except:
        continue

repo_data_list = []
for data in json_data:
    for keyword_data in data.keyword_data_list:
        for commit_data in keyword_data.commit_data_list:
            patch = commit_data.patch
            msg = commit_data.msg
            if 'optimize' in msg or 'optimization' in msg:
                msg='optimization'
            elif 'perf' in msg:
                msg='performance'
            elif 'time' in msg and 'complexity' in msg:
                msg='time complexity'

            get_patch_dict(patch, msg)

# for i, data in enumerate(data_manager.data_list):
#     print(f'### {i}')
#     print('old')
#     print(data.old)
#     print('new')
#     print(data.new)
#     print()
#     print('comment')
#     print(data.comment)
    
data_manager.save()
