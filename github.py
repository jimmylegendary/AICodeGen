from genericpath import isfile
import requests
import time
import os
import wget
from dotenv import load_dotenv
# from CodeDatabase import *
import subprocess
from util import *

import urllib.request
import json

load_dotenv()


API_KEY_LIST = json.loads(os.environ.get('GITHUB_PATS'))
API_KEY_INDEX = 0
API_KEY = API_KEY_LIST[API_KEY_INDEX]

perf_keywords = [
            'perf',
            'optimization',
            'time complexity',
        ]

def get_next_api_key():
    global API_KEY_INDEX, API_KEY
    API_KEY_INDEX = (API_KEY_INDEX + 1) % len(API_KEY_LIST)
    API_KEY = API_KEY_LIST[API_KEY_INDEX]

def get_api_call(type, attr):
    cmd = ['curl','-H', f'Authorization: token {API_KEY}', 'https://api.github.com/rate_limit']
    r = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = r.communicate()
    r = requests.Response()
    r._content = output
    r.status_code = 200
    if type == 'rate':
        api_attr = r.json()['rate'][attr]
    else:
        api_attr = r.json()['resources'][type][attr]
    
    return api_attr

API_count = get_api_call(type='rate', attr='used')
search_count = get_api_call(type='search', attr='used')
limit = get_api_call(type='rate', attr='limit')
search_limit = get_api_call(type='search', attr='limit')
def try_curl(TARGET):
    cmd = ['curl','-s', f'https://{API_KEY}@{TARGET[8:]}']
    # print(cmd)
    r = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = r.communicate()
    assert output != '' and output != None, f'Request fail for {TARGET}'
    r = requests.Response()
    r._content = output
    r.status_code = 200
    
    global API_count
    API_count += 1
    
    return r
def wait_github_api_limit(type):
    global API_count, limit, search_count, search_limit
    print(f'API_count : {API_count}, limit : {limit}')
    print(f'search_count : {search_count}, search_limit : {search_limit}')
    
    for _ in range(len(API_KEY_LIST)):
        get_next_api_key()
        remaining_call = int(get_api_call(type=type, attr='remaining'))
        print(f'API_KEY_INDEX {API_KEY_INDEX} remaining_call {remaining_call}')
        if remaining_call != 0:
            API_count = get_api_call(type='rate', attr='used')
            search_count = get_api_call(type='search', attr='used')
            return
    
    reset_timestamp = get_api_call(type=type, attr='reset')
    
    delay = max(reset_timestamp - time.time(), 0) + 1
    print(f'wait {delay} seconds...')
    time.sleep(delay)
    if type == 'rate':
        limit = get_api_call(type=type, attr='limit')
        API_count = 0
    elif type == 'search':
        search_limit = get_api_call(type=type, attr='limit')
        search_count = 0

def try_request(TARGET, headers):
    global API_count, limit
    global search_count

    type = 'rate'
    if 'search' in TARGET:
        type = 'search'
        search_count += 1

    if search_count >= search_limit - 2:
        wait_github_api_limit('search')
        
    if API_count >= limit - 2:
        wait_github_api_limit('rate')
    
    tried = 0
    r = None
    # print(TARGET)
    DELAY = 1
    # time.sleep(DELAY)
    while tried < 3:
        try:
            r = requests.get(TARGET,headers=headers)
            API_count += 1
            print(f'API call count {API_count}', r.status_code)
            if r.status_code == 200:
                # curl -I https://api.github.com/users/octocat -u jimmylegendary:{PAT}
                if 'json' not in r.headers.get('content-type'):
                    print(r.headers.get('content-type'), TARGET)
                break
            else:
                print(TARGET)
                json_data = r.json()
                if 'message' in json_data and 'API rate limit exceeded' in json_data['message']:
                    print(json_data['message'])
                    tried += 1
                    wait_github_api_limit(type)
            tried += 1
        except:
            # print(get_ramaining_api_call())
            assert False, r.status_code
            tried+=1
        print(f'{tried} times tried', f'wait {DELAY} seconds...')
        time.sleep(DELAY)
    return r

class SegQuery:
    def __init__(self, start, end, step):
        self.start = start
        self.end = end
        self.step = step
        
    def get_query(self, prefix, sufix):
        query = prefix
        if self.step == -1:
            query += f'>={self.start}'
            query += sufix
            return query
        else:
            for i in range(self.start, self.end, self.step):
                query = prefix
                range_start = i
                range_end = range_start + self.step
                query += f'{range_start}..{range_end}'
                query += sufix
                
                yield query

class PyGithub:
    # curl -H 'Authorization: token {PAT}' https://api.github.com/rate_limit
    def __init__(self):
        self.API_root = 'http://api.github.com'
        self.API_REPO_root = 'https://api.github.com/repos'
        # root/{repo}/{sha}/{path2file}
        self.API_CODE_root = 'https://raw.githubusercontent.com'
        self.API_KEY = API_KEY
        self.headers = {
            'Accept' : 'application/vnd.github+json',
            'Authorization': f'token {self.API_KEY}'
        }
        self.repos = []
        # self.code_database = CodeDatabase()
        self.json_data = JsonData()
        self.seg_query_by_keword = {
            'q=language:cpp+stars:': [
                SegQuery(100,1000,5),
                SegQuery(1000,10000,1000),
                SegQuery(10000,10001,-1),
            ]
        }
    
    def get_api_headers(self):
        return {
            'Accept' : 'application/vnd.github+json',
            'Authorization': f'token {API_KEY}'
        }

    def search_repo(self):
        SEARCH_REPOSITORY='search/repositories'
        REPO_QUERY='q=language:cpp+stars:>=10000&sort=stars&order=desc&per_page=100&page='
        TARGET=self.API_root+'/'+SEARCH_REPOSITORY+'?'+REPO_QUERY
        repo_list : list[RepoData] = []
        keyword = 'q=language:cpp+stars:'
        sufix = '&sort=stars&order=desc&per_page=100&page='
        seq_query_list = []
        for seq_query in self.seg_query_by_keword[keyword]:
            queries = seq_query.get_query(keyword, sufix)
            for query in queries:
                seq_query_list.append(query)
        
        repo_count = 0
        seq_query_list = self.seg_query_by_keword[keyword]
        for seg_query in seq_query_list:
            start, end, step = seg_query.start, seg_query.end, seg_query.step
            range_start = start
            range_end = range_start + step
            while range_end <= end:
                if step == -1:
                    query = keyword + f'>={range_start}' + sufix
                else:
                    query = keyword + f'{range_start}..{range_end}' + sufix
                page_idx = 1
                TARGET=self.API_root+'/'+SEARCH_REPOSITORY+'?'+ query
                max_page = 10
                while(page_idx <= max_page):
                    r = try_request(f'{TARGET}{page_idx}',headers=self.get_api_headers())
                    json_data = r.json()
                    if page_idx == 1:
                        max_page = int(json_data['total_count']) if 'total_count' in json_data else 0
                        max_page = max_page // 100 if max_page % 100 == 0 else (max_page // 100) + 1
                        max_page = min(max_page, 10)
                        print('max_page', max_page)
                    if page_idx > max_page: break
                    for content in r.json()['items']:
                        # self.repos.append(json.loads(content, object_hook=lambda d: SimpleNamespace(**d)))
                        repo_list.append(RepoData(content['full_name']))
                        repo_count += 1
                        # print(content['clone_url'])
                        # if repo_count >= 20:
                        #     return repo_list
                    page_idx += 1
                
                if step == -1:
                    break
                
                if max_page <= 5:
                    step *= 2
                range_start = range_end
                range_end = min(range_start + step, end)
                if range_start == range_end: break
        return repo_list
    
    def get_commit_history4file(self, repo, path2file):
        TARGET= self.API_REPO_root + '/'+ repo+'/commits?path='+path2file
        r = try_request(TARGET,headers=self.get_api_headers())
        
        if len(r.json()) == 0:
            print('commit_history4file_list size is 0 for ', TARGET)
        
        return r.json()
    
    def get_code_file(self, repo, sha, path2file):
        TARGET=self.API_CODE_root + '/' + repo + '/' + sha + '/' + path2file
        r = try_request(TARGET,headers=self.get_api_headers())
        
        return r.content
    
    def get_code_link(self, repo, sha, path2file):
        TARGET=self.API_CODE_root + '/' + repo + '/' + sha + '/' + path2file
        try:
            res = urllib.request.urlopen(TARGET)
            if res.status != 200:
                TARGET = ''
        except:
            TARGET = ''
        
        return TARGET

    def search_commits(self, repo_name, keyword):
        commit_data_list : list[CommitData] = []
        SEARCH_COMMIT='search/commits'
        COMMIT_QUERY=f'q=repo:{repo_name}+{keyword}'
        OPTIONS='&sort=committer-date&order=desc&per_page=100&page='
        TARGET=self.API_root+'/'+SEARCH_COMMIT+'?'+COMMIT_QUERY+OPTIONS
        
        ignore_keywords = ['Merge pull request']

        count=0
        page_idx = 1
        max_commit = 100
        while(count < max_commit):
            r = try_request(f'{TARGET}{page_idx}',headers=self.get_api_headers())
            if r == None:
                break
            if (r.status_code != 200) or ('json' not in r.headers.get('content-type')) :
                break
            if count == 0:
                max_commit = min(r.json()['total_count'],500)
                if max_commit == 0:
                    break
                print(f'{repo_name} has', r.json()['total_count'], 'commits')
                
            idx = 1
            start = False
            rjson = r.json()
            for content in rjson['items']:
                msg = content['commit']['message']
                commit_sha = content['sha']
                # flag = False
                # for keyword in keywords:
                #     flag = flag or keyword in msg
                # if flag == False:
                #     continue

                if idx == 1:
                    start = True
                    print(f'START {repo_name}')
                    
                is_ignore = False
                for ig_keyword in ignore_keywords:
                    if ig_keyword in msg:
                        is_ignore = True
                
                if is_ignore == True:
                    continue

                if len(msg) < 500:
                    # print(f'commit{idx}', msg)
                    TARGET = self.API_REPO_root + '/' + repo_name + '/commits/' + commit_sha
                    r = try_request(TARGET,headers=self.get_api_headers())
                    if r.status_code != 200:
                        continue
                    for item in r.json()['files']:
                        path2file = item['filename']
                        sufix = path2file.split('.')[-1]
                        # if sufix != 'c':
                        if sufix != 'cpp' and \
                            sufix != 'cc' and \
                            sufix != 'c++' and \
                            sufix != 'cp' and \
                            sufix != 'cxx' and \
                            sufix != 'CPP':
                            continue
                        # print(path2file)
                        patch = item['patch'] if 'patch' in item else ''
                        commit_history4file_list = self.get_commit_history4file(repo_name, path2file)
                        prev_file_idx = 0
                        if len(commit_history4file_list) == 0:
                            continue
                            
                        while prev_file_idx < len(commit_history4file_list):
                            if commit_history4file_list[prev_file_idx]['sha'] == commit_sha:
                                prev_file_idx += 1
                                break
                            prev_file_idx += 1
                        if prev_file_idx >= len(commit_history4file_list):
                            prev_file_idx = len(commit_history4file_list) - 1
                        prev_commit_sha = commit_history4file_list[prev_file_idx]['sha']
                        curr_commit_sha = commit_sha
                        # prev_code = self.get_code_file(repo, prev_commit_sha, path2file)
                        # curr_code = self.get_code_file(repo, curr_commit_sha, path2file)
                        
                        prev_code_link = self.get_code_link(repo_name, prev_commit_sha, path2file)
                        curr_code_link = self.get_code_link(repo_name, curr_commit_sha, path2file)
                        if prev_code_link != '' and curr_code_link != '' and patch != '' and msg != '':
                            # self.code_database.append(
                            #     CodeData(prev_code, path2file, prev_commit_sha, patch, msg),
                            #     CodeData(curr_code, path2file, curr_commit_sha, patch, msg)
                            #     )
                            # input = CodeData(prev_code, path2file, prev_commit_sha)
                            # golden = CodeData(curr_code, path2file, curr_commit_sha)
                            # self.code_database.append_review_data(
                            #     ReviewData(input, golden, patch, msg)
                            #     ) 
                            global commit_data_size
                            commit_data_size += 1
                            print('commit_data_size',commit_data_size)
                            commit_data = CommitData(
                                hash=commit_sha, 
                                old_file=prev_code_link,
                                new_file=curr_code_link,
                                msg=msg,
                                patch=patch
                            )
                            commit_data_list.append(commit_data)                   
                idx += 1

            if start == True:
                print(f'END {repo.repo_name}\n')
            count += rjson['total_count']
            page_idx += 1
        
        return commit_data_list[:]

pygithub = PyGithub()
repo_file = 'repo.list'
if os.path.isfile(repo_file):
    repo_list = []
    with open(repo_file, 'r') as f:
        for line in f.readlines():
            repo_list.append(RepoData(line.strip('\n')))
        f.close()
else:
    repo_list = pygithub.search_repo()
    with open(repo_file, 'w') as f:
        for repo in repo_list:
            f.write(repo.repo_name + '\n')
        f.close()
        
outfile = 'output.jsonl'
commit_data_size = 0
repo_data_size = 0
repo_checked = 0
if os.path.isfile(outfile):
    data_list = [json.loads(line) for line in open(outfile)]
    except_repo_list = list(map(lambda d:d['repo_name'], data_list))
    for data in data_list:
        repo_data_size += 1
        for keyword_data in data['keyword_data_list']:
            commit_data_size += len(keyword_data['commit_data_list'])
else:
    data_list = []
    except_repo_list = []

skip_list = {}
for keyword in perf_keywords:
    try:
        with open(f'{keyword}.skip','r') as f:
            skip_repo_list = []
            for line in f.readlines():
                skip_repo_list.append(line.strip('\n'))
            skip_list[keyword] = skip_repo_list
    except:
        continue

for repo in repo_list:
    repo_checked += 1
    repo_name = repo.repo_name
    if repo_name in except_repo_list:
        continue
    try:
        for keyword in perf_keywords:
            if keyword in skip_list and repo_name in skip_list[keyword]: continue
            keyword_data = KeywordData(keyword)
            commit_data_list = pygithub.search_commits(repo_name, keyword_data.keyword)
            if len(commit_data_list) > 0:
                keyword_data.push_back(commit_data_list=commit_data_list)
                repo.push_back(keyword_data=keyword_data)
            else:
                with open(f'{keyword}.skip','a') as f:
                    f.write(repo_name+'\n')
                    f.close()
    except:
        assert False, 'ERROR!!!!!!!'
    if len(repo.keyword_data_list) > 0:
        repo.write_json(outfile)
        pygithub.json_data.push_back(repo)
        repo_data_size += 1
        data_list.append(repo.toJson())
    print('repo_checked', repo_checked, 'repo_data_size', repo_data_size, 'commit_data_size', commit_data_size)

# pygithub.code_database.download_review_data()

