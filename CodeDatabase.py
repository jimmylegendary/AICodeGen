import wget

class CodeData:
    def __init__(self, link, path2file : str):
        # path2file : tensorflow/lite/tools/benchmark/benchmark_performance_options.cc
        self.link = link
        self.raw_code = ''
        self.path = '/'.join(path2file.split('/')[:-1])
        
    def download(self):
        wget.download(self.link, out=self.path)

class CodeDatabase:
    def __init__(self):
        self.input_list : list[CodeData] = []
        self.golden_list : list[CodeData] = []
        self.pair_list : list[tuple[CodeData]] = []