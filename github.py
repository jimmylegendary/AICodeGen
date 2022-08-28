import requests
import time
import os
import wget
from dotenv import load_dotenv
from CodeDatabase import *
import subprocess

import urllib.request

load_dotenv()


API_count = 0
API_KEY = os.environ.get('GITHUB_PAT')

perf_keywords = [
            'perf'
        ]

def get_ramaining_api_call():
    cmd = ['curl','-H', f'Authorization: token {API_KEY}', 'https://api.github.com/rate_limit']
    r = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = r.communicate()
    r = requests.Response()
    r._content = output
    r.status_code = 200
    remaining_call = r.json()['rate']['remaining']
    
    return remaining_call

limit = get_ramaining_api_call()
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
def wait_github_api_limit():
    global API_count, limit
    print(f'API_count : {API_count}, limit : {limit}')
    if API_count < limit:
        assert False, f'API_count : {API_count} is under limit : {limit}'
        
    cmd = ['curl','-H', f'Authorization: token {API_KEY}', 'https://api.github.com/rate_limit']
    # print(' '.join(cmd))
    r = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = r.communicate()
    r = requests.Response()
    r._content = output
    r.status_code = 200
    
    reset_timestamp = r.json()['rate']['reset']
    delay = reset_timestamp - time.time()
    print(f'wait {delay} seconds...')
    time.sleep(delay+1)
    limit = get_ramaining_api_call()
    API_count = 0

search_count = 0
def try_request(TARGET, headers):
    global API_count, limit
    global search_count

    if 'search' in TARGET:
        search_count += 1
        print(f'search_count : {search_count}')
        print(f'TARGET: {TARGET}')
    if API_count >= limit:
        print(TARGET)
        wait_github_api_limit()
    
    tried = 0
    r = None
    # print(TARGET)
    DELAY = 0.01
    # time.sleep(DELAY)
    while tried < 1:
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
                # print(TARGET,headers)
                # print(r.json())
                if 'API rate limit exceeded' in r.json()['message']:
                    print(TARGET)
                    tried += 1
                    continue
                    wait_github_api_limit()
                else:
                    assert False
            tried += 1
        except:
            print(get_ramaining_api_call())
            assert False, r.status_code
            tried+=1
        print(f'{tried} times tried', f'wait {DELAY} seconds...')
        print(TARGET,headers)
        time.sleep(DELAY)
    return r

class SegQuery:
    def __init__(self, start, end, step):
        self.start = start
        self.end = end
        self.step = step
        
    def get_query(self, prefix, sufix):
        query = prefix
        if self.end == -1:
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
        self.API_KEY = os.environ.get('GITHUB_PAT')
        self.headers = {
            'Accept' : 'application/vnd.github+json',
            'Authorization': f'token {self.API_KEY}'
        }
        self.repos = []
        self.code_database = CodeDatabase()
        self.seg_query_by_keword = {
            'q=language:cpp+stars:': [
                SegQuery(100,1000,5),
                SegQuery(1000,10000,1000),
                SegQuery(10000,-1,-1),
            ]
        }

    def search_repo(self):
        SEARCH_REPOSITORY='search/repositories'
        REPO_QUERY='q=language:cpp+stars:>=10000&sort=stars&order=desc&per_page=100&page='
        TARGET=self.API_root+'/'+SEARCH_REPOSITORY+'?'+REPO_QUERY
        repo_list = []
        keyword = 'q=language:cpp+stars:'
        sufix = '&sort=stars&order=desc&per_page=100&page='
        seq_query_list = []
        for seq_query in self.seg_query_by_keword[keyword]:
            queries = seq_query.get_query(keyword, sufix)
            for query in queries:
                seq_query_list.append(query)
        
        repo_count = 0
        for query in seq_query_list:
            page_idx = 1
            TARGET=self.API_root+'/'+SEARCH_REPOSITORY+'?'+ query
            max_page = 10
            while(page_idx <= max_page):
                r = try_request(f'{TARGET}{page_idx}',headers=self.headers)
                if page_idx == 1:
                    max_page = int(r.json()['total_count'])
                    max_page = max_page // 100 if max_page % 100 == 0 else (max_page // 100) + 1
                    max_page = min(max_page, 10)
                for content in r.json()['items']:
                    # self.repos.append(json.loads(content, object_hook=lambda d: SimpleNamespace(**d)))
                    repo_list.append(content['full_name'])
                    repo_count += 1
                    # print(content['clone_url'])
                    if repo_count >= 20:
                        return repo_list
                page_idx += 1

        return repo_list
    
    def get_commit_history4file(self, repo, path2file):
        TARGET= self.API_REPO_root + '/'+ repo+'/commits?path='+path2file
        r = try_request(TARGET,headers=self.headers)
        
        if len(r.json()) == 0:
            print('commit_history4file_list size is 0 for ', TARGET)
        
        return r.json()
    
    def get_code_file(self, repo, sha, path2file):
        TARGET=self.API_CODE_root + '/' + repo + '/' + sha + '/' + path2file
        r = try_request(TARGET,headers=self.headers)
        
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

    def search_commits(self, repo, keyword):
        SEARCH_COMMIT='search/commits'
        COMMIT_QUERY=f'q=repo:{repo}+{keyword}'
        OPTIONS='&sort=committer-date&order=desc&per_page=100&page='
        TARGET=self.API_root+'/'+SEARCH_COMMIT+'?'+COMMIT_QUERY+OPTIONS
        
        ignore_keywords = ['Merge pull request']

        count=0
        page_idx = 1
        max_commit = 100
        while(count < max_commit):
            r = try_request(f'{TARGET}{page_idx}',headers=self.headers)
            if r == None:
                break
            if (r.status_code != 200) or ('json' not in r.headers.get('content-type')) :
                break
            if count == 0:
                max_commit = min(r.json()['total_count'],500)
                if max_commit == 0:
                    break
                print(f'{repo} has', r.json()['total_count'], 'commits')
                
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
                    print(f'START {repo}')
                    
                is_ignore = False
                for ig_keyword in ignore_keywords:
                    if ig_keyword in msg:
                        is_ignore = True
                
                if is_ignore == True:
                    continue

                if len(msg) < 500:
                    # print(f'commit{idx}', msg)
                    TARGET = self.API_REPO_root + '/' + repo + '/commits/' + commit_sha
                    r = try_request(TARGET,headers=self.headers)
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
                        commit_history4file_list = self.get_commit_history4file(repo, path2file)
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
                        
                        prev_code = self.get_code_link(repo, prev_commit_sha, path2file)
                        curr_code = self.get_code_link(repo, curr_commit_sha, path2file)
                        if prev_code != '' and curr_code != '' and patch != '' and msg != '':
                            # self.code_database.append(
                            #     CodeData(prev_code, path2file, prev_commit_sha, patch, msg),
                            #     CodeData(curr_code, path2file, curr_commit_sha, patch, msg)
                            #     )
                            input = CodeData(prev_code, path2file, prev_commit_sha)
                            golden = CodeData(curr_code, path2file, curr_commit_sha)
                            self.code_database.append_review_data(
                                ReviewData(input, golden, patch, msg)
                                )                            
                        
                idx += 1

            if start == True:
                print(f'END {repo}\n')
            count += rjson['total_count']
            page_idx += 1

pygithub = PyGithub()
repo_list = pygithub.search_repo()
for repo in repo_list:
    for keyword in perf_keywords:
        pygithub.search_commits(repo, keyword)

pygithub.code_database.download_review_data()