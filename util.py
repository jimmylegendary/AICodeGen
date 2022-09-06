import json

class CommitData:
    def __init__(self, hash, old_file, new_file, msg, patch):
        self.hash = hash
        self.old_file = old_file
        self.new_file = new_file
        self.msg = msg
        self.patch = patch

class KeywordData:
    def __init__(self, keyword):
        self.keyword = keyword
        self.commit_data_list : list[CommitData] = []
    
    def push_back(self, commit_data_list : list[CommitData]):
        if isinstance(commit_data_list, list):
            self.commit_data_list.extend(commit_data_list)
        elif isinstance(commit_data_list, CommitData):
            self.commit_data_list.append(commit_data_list)
        else:
            assert False, "commit_data is wrong"

class RepoData:
    def __init__(self, repo_name):
        self.repo_name = repo_name
        self.keyword_data_list : list[KeywordData] = []
    
    def push_back(self, keyword_data : KeywordData):
        has_data = False
        for data in self.keyword_data_list:
            if data.keyword == keyword_data.keyword:
                has_data = True
                data_idx = self.keyword_data_list.index(data)
                break
        if has_data:
            self.keyword_data_list[data_idx].push_back(keyword_data.commit_data_list)
        else:
            self.keyword_data_list.append(keyword_data)
            
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True)
        
    def write_json(self, out_file):
        with open(out_file, 'a+', encoding='utf-8') as f:
            f.write(self.toJson() + '\n')
            f.close()
        
class JsonData:
    def __init__(self):
        self.repo_data_list : list[RepoData] = []
        
    def push_back(self, repo_data : RepoData):
        has_data = False
        for data in self.repo_data_list:
            if data.repo_name == repo_data.repo_name:
                has_data = True
                data_idx = self.repo_data_list.index(data)
                break
        if has_data:
            for keyword_data in repo_data.keyword_data_list:
                self.repo_data_list[data_idx].push_back(keyword_data)
        else:
            self.repo_data_list.append(repo_data)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True)
        
    def write_json(self, out_file):
        with open(out_file, 'w', encoding='utf-8') as f:
            for repo_data in self.repo_data_list:
                f.write(repo_data.toJson() + '\n')
            f.close()