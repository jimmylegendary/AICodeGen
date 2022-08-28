import wget
import os

class ReviewData:
    def __init__(self, input, golden, patch, msg):
        self.input : CodeData = input
        self.golden : CodeData = golden
        self.patch : str = patch
        self.msg : str = msg
    
    def download(self, root = '.'):
        self.input.download(root+'/input')
        self.golden.download(root+'/golden')
        patch_path = f'{root}/patch'
        with open(patch_path, 'w') as f:
            f.write(self.patch)
            f.close()
        msg_path = f'{root}/msg'
        with open(msg_path, 'w') as f:
            f.write(self.msg)
            f.close()
    
class CodeData:
    def __init__(self, link, path2file, sha):
        # path2file : tensorflow/lite/tools/benchmark/benchmark_performance_options.cc
        self.link = link
        self.raw_code = ''
        self.path = '/'.join(path2file.split('/')[:-1])
        self.sha = sha
        
    def download(self, root = '.'):
        out=f'{root}/{self.sha}/{self.path}'
        os.makedirs(out,exist_ok=True)
        wget.download(self.link, out=out)

class CodeDatabase:
    def __init__(self):
        self.pair_list : list[tuple[CodeData]] = []
        self.review_data_list : list[ReviewData] = []
        
    def append(self, input, golden):
        self.pair_list.append((input, golden))
        print('Datasize :', len(self.pair_list))
        
    def download_review_data(self):
        root = 'pair_data'
        for idx, pair in enumerate(self.pair_list):
            pair[0].download(f'{root}/{idx}/input')
            pair[1].download(f'{root}/{idx}/golden')
        
    def append_review_data(self, review_data):
        self.review_data_list.append(review_data)
        print('Datasize :', len(self.review_data_list))
        
    def download_review_data(self):
        root = 'pair_data'
        for idx, review_data in enumerate(self.review_data_list):
            review_data.download(f'{root}/{idx}')