import os

patch_file_list = []
patch_data_list = []
def get_patch_dict(filename):
    # file = open(filename,'rt', encoding='UTF-8')
    # tree = parser.parse(bytes(file.read(),"utf8"))
    # file = open(filename,'rt')
    with open(filename,'r') as f:
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
                    if lines[idx][0] == '-':
                        old_patch_str += lines[idx]
                    if lines[idx][0] == '+':
                        new_patch_str += lines[idx]
                    else:
                        print(lines[idx][0])
                        old_patch_str += lines[idx]
                        new_patch_str += lines[idx]
                    old_patch_str += '\n'
                    new_patch_str += '\n'
                patch_data_list.append((old_patch_str, new_patch_str))

root_dirt = 'pair_data'
for i in range(34):
    root_dir = 'pair_data/' + str(i)
    for (root, dirs, files) in os.walk(root_dir):
        if len(files) > 0:
            for file_name in files:
                if file_name == 'patch':
                    patch_file_list.append(root + '/' + file_name)

for file in patch_file_list:
    get_patch_dict(file)

for i, data in enumerate(patch_data_list):
    print(f'### {i}')
    print('old')
    print(data[0])
    print('new')
    print(data[1])
    print()