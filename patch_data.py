import os
import json

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

def get_patch_dict(patch_filename, msg_filename):
    # file = open(filename,'rt', encoding='UTF-8')
    # tree = parser.parse(bytes(file.read(),"utf8"))
    # file = open(filename,'rt')
    
    msg = ''
    with open(msg_filename,'r') as f:
        msg = f.read()
        f.close()
    
    with open(patch_filename,'r') as f:
        count = 0
        lines = f.readlines()
        lines = [line for raw_line in lines for line in raw_line.split('\n')]
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

root_dirt = 'pair_data'
for i in range(45):
    root_dir = 'pair_data/' + str(i)
    for (root, dirs, files) in os.walk(root_dir):
        if len(files) > 0 and 'patch' in files and 'msg' in files:
            for file_name in files:
                if file_name == 'patch':
                    patch_file = f'{root}/{file_name}'
                elif file_name == 'msg':
                    msg_file = f'{root}/{file_name}'
            get_patch_dict(patch_file, msg_file)
        
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