from util import *

commit_data1 = CommitData('0','1','2','3','4')
commit_data2 = CommitData('5','6','7','8','9')
keyword = 'perf'
keyword_data = KeywordData(keyword)
repo_name = 'pytorch'
repo_data = RepoData(repo_name)
json_data = JsonData()

keyword_data.push_back(commit_data1)
keyword_data.push_back(commit_data2)
repo_data.push_back(keyword_data)
json_data.push_back(repo_data)

json_file = 'output.jsonl'
json_data.write_json(json_file)
    
repo_name = 'tensorflow'
repo_data = RepoData(repo_name)
repo_data.push_back(keyword_data)

repo_data.write_json(json_file)

data = [json.loads(line) for line in open(json_file)]
for d in data:
    print('repo_name', d['repo_name'])
    keyword_data_list = d['keyword_data_list']
    for kdata in keyword_data_list:
        print('keyword', kdata['keyword'])
        for cdata in kdata['commit_data_list']:
            print(cdata)
    