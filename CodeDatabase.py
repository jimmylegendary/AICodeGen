class CodeData:
    def __init__(self):
        self.link = ''
        self.raw_code = ''

class CodeDatabase:
    def __init__(self):
        self.input_list : list[CodeData] = []
        self.golden_list : list[CodeData] = []
        self.pair_list : list[tuple[CodeData]] = []