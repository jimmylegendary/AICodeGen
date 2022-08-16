from tree_sitter import Parser, Language
import os

func_data_size = 0

def get_func_dict(filename, ):
    # file = open(filename,'rt', encoding='UTF-8')
    # tree = parser.parse(bytes(file.read(),"utf8"))
    # file = open(filename,'rt')
    with open(filename,'rb') as f:
        tree = parser.parse(bytes(f.read()))
    node_list = [tree.root_node]
    fun_dec = ''
    fun_def = ''
    func_dict = {}
    while len(node_list) != 0:
        node = node_list.pop()
        try:
            for child in node.children:
                node_list.append(child)
        except:
            continue
        if node.type == 'function_definition':
            # fun_def = node.text.decode('utf-8')
            fun_def = node.text
        if fun_def != '' and node.type == 'function_declarator':
            # fun_dec = node.text.decode('utf-8')
            fun_dec = node.text
            func_dict[fun_dec] = fun_def
            fun_def = ''
            fun_dec = ''

    return func_dict

def write_func_files(func_file_path, input, golden):
    global func_data_size
    os.makedirs(func_file_path,exist_ok=True)
    # with open(func_file_path + '/input','w',encoding='utf-8') as f:
    with open(func_file_path + '/input','wb') as f:
        f.write(input)
    f.close()
    # with open(func_file_path + '/golden','w',encoding='utf-8') as f:
    with open(func_file_path + '/golden','wb') as f:
        f.write(golden)
    f.close()
    func_data_size += 1

Language.build_library(
  # Store the library in the `build` directory
  'build/my-languages.so',

  # Include one or more languages
  [
    'vendor/tree-sitter-cpp'
  ]
)

CPP_LANGUAGE = Language('build/my-languages.so', 'cpp')

parser = Parser()
parser.set_language(CPP_LANGUAGE)



input_file_list = []
golden_file_list = []
for i in range(1504):
    root_dir = 'pair_data/golden/' + str(i)
    for (root, dirs, files) in os.walk(root_dir):
        if len(files) > 0:
            for file_name in files:
                golden_file_list.append(root + '/' + file_name)
    root_dir = 'pair_data/input/' + str(i)
    for (root, dirs, files) in os.walk(root_dir):
        if len(files) > 0:
            for file_name in files:
                input_file_list.append(root + '/' + file_name)
for input,golden in zip(input_file_list, golden_file_list):
    merged_func_dict = {}
    try:
        input_func_dict = get_func_dict(input)
    except Exception as e:
            print(type(e).__name__)
            print(str(e))
            print(input)
            exit(1)
    try:
        golden_func_dict = get_func_dict(golden)
    except Exception as e:
            print(type(e).__name__)
            print(str(e))
            print(golden)
            exit(1)
    for k,v in golden_func_dict.items():
        if k in input_func_dict and v != input_func_dict[k]:
            merged_func_dict[k] = (input_func_dict[k],v)

    for k,(input,golden) in merged_func_dict.items():
        # print('Function',k)
        # print(input)
        # print(golden)
        func_file_path = f'func_data/{func_data_size}'
        try:
            write_func_files(func_file_path, input, golden)
        except Exception as e:
            print(type(e).__name__)
            exit(1)