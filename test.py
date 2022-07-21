import requests
import json
from types import SimpleNamespace
import time
import os
import wget

def try_request(TARGET, headers):
    tried = 0
    r = None
    print(TARGET)
    DELAY = 10
    time.sleep(DELAY)
    while tried < 3:
        try:
            r = requests.get(TARGET,headers=headers)
            if r.status_code == 200:
                break
            tried += 1
        except:
            tried+=1
        print(f'{tried} times tried', f'wait {DELAY} seconds...')
        time.sleep(DELAY)
    return r

class PyGithub:
    def __init__(self):
        self.API_root = 'http://api.github.com'
        self.API_REPO_root = 'https://api.github.com/repos'
        # root/{repo}/{sha}/{path2file}
        self.API_CODE_root = 'https://raw.githubusercontent.com'
        self.API_KEY = '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'
        self.headers = {
            'Accept' : 'application/vnd.github+json',
            'Authorization': self.API_KEY
        }
        self.repos = []

    def search_repo(self):
        SEARCH_REPOSITORY='search/repositories'
        REPO_QUERY='q=language:C++&sort=stars&order=desc&per_page=100&page='
        TARGET=self.API_root+'/'+SEARCH_REPOSITORY+'?'+REPO_QUERY
        repo_list = []
        page_idx = 1
        while(page_idx <= 1):
            r = try_request(f'{TARGET}{page_idx}',headers=self.headers)
            for content in r.json()['items']:
                # self.repos.append(json.loads(content, object_hook=lambda d: SimpleNamespace(**d)))
                repo_list.append(content['full_name'])
                # print(content['clone_url'])
            page_idx += 1

        return repo_list
    
    def get_commit_history4file(self, repo, path2file):
        TARGET= self.API_REPO_root + '/'+ repo+'/commits?path='+path2file
        print(TARGET)
        r = try_request(TARGET,headers=self.headers)
        
        return r.json()
    
    def get_code_file(self, repo, sha, path2file):
        TARGET=self.API_CODE_root + '/' + repo + '/' + sha + '/' + path2file
        r = try_request(TARGET,headers=self.headers)
        
        return r.content
    
    def save_code_file(self, repo, sha, path2file):
        TARGET=self.API_CODE_root + '/' + repo + '/' + sha + '/' + path2file
        wget.download(TARGET)

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
            if r.status_code != 200:
                break
            if count == 0:
                max_commit = min(r.json()['total_count'],500)
                if max_commit == 0:
                    break
                print(f'{repo} has', r.json()['total_count'], 'commits')
                
            idx = 1
            start = False
            for content in r.json()['items']:
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
                        if sufix != 'cpp' and sufix != 'c':
                            continue
                        print(path2file)
                        commit_history4file_list = self.get_commit_history4file(repo, path2file)
                        prev_file_idx = 0
                        while prev_file_idx < len(commit_history4file_list):
                            if commit_history4file_list[prev_file_idx]['sha'] == commit_sha:
                                prev_file_idx += 1
                                break
                            prev_file_idx += 1
                        if prev_file_idx >= len(commit_history4file_list):
                            prev_file_idx = len(commit_history4file_list) - 1
                        prev_commit_sha = commit_history4file_list[prev_file_idx]['sha']
                        curr_commit_sha = commit_sha
                        prev_code = self.get_code_file(repo, prev_commit_sha, path2file)
                        curr_code = self.get_code_file(repo, curr_commit_sha, path2file)
                        prj_dir = os.getcwd()
                        fd = os.open(prj_dir +'/old_'+path2file.split('/')[-1], os.O_RDWR|os.O_CREAT)
                        os.write(fd,prev_code)
                        os.close(fd)
                        fd = os.open(prj_dir +'/new_'+path2file.split('/')[-1], os.O_RDWR|os.O_CREAT)
                        os.write(fd,curr_code)
                        os.close(fd)
                        print(f'{repo}/{path2file} is saved')
                        
                idx += 1

            if start == True:
                print(f'END {repo}\n')
            count += len(r.json()['items'])
            page_idx += 1

pygithub = PyGithub()
tried = 0
while tried < 10:
    try:
        repo_list = pygithub.search_repo()
        break
    except:
        tried+=1
        print(f'{tried} times tried', 'wait 5 seconds...')
        time.sleep(5)

for repo in repo_list:
    try:
        keywords = [
            'perf'
        ]
        for keyword in keywords:
            pygithub.search_commits(repo, keyword)
    except:
        # print(f'{repo} has no commits')
        pass