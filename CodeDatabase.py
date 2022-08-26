import wget
import os

class CodeData:
    def __init__(self, link, path2file, sha, patch):
        # path2file : tensorflow/lite/tools/benchmark/benchmark_performance_options.cc
        self.link = link
        self.raw_code = ''
        self.path = '/'.join(path2file.split('/')[:-1])
        self.sha = sha
        self.patch = patch
        
    def download(self, root = '.'):
        out=f'{root}/{self.sha}/{self.path}'
        os.makedirs(out,exist_ok=True)
        patch_path = f'{root}/../patch'
        with open(patch_path, 'w') as f:
            f.write(self.patch)
            f.close()
        wget.download(self.link, out=out)

class CodeDatabase:
    def __init__(self):
        # self.input_list : list[CodeData] = []
        # self.golden_list : list[CodeData] = []
        self.pair_list : list[tuple[CodeData]] = []
        
    def append(self, input, golden):
        self.pair_list.append((input, golden))
        print('Datasize :', len(self.pair_list))
        
    def download(self):
        root = 'pair_data'
        for idx, pair in enumerate(self.pair_list):
            pair[0].download(f'{root}/{idx}/input')
            pair[1].download(f'{root}/{idx}/golden')