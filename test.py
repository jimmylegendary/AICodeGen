import requests
import json
from types import SimpleNamespace


class PyGithub:
    def __init__(self):
        self.API_root = 'http://api.github.com'
        self.API_KEY = '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'
        self.headers = {
            'Accept' : 'application/vnd.github+json',
            'Authorization': self.API_KEY
        }
        self.repos = []

    def search_repo(self):
        SEARCH_REPOSITORY='search/repositories'
        REPO_QUERY='q=C++&sort=stars&order=desc&per_page=100&page=3'
        TARGET=self.API_root+'/'+SEARCH_REPOSITORY+'?'+REPO_QUERY
        repo_list = []
        idx = 0
        while(idx < 300):
            r = requests.get(TARGET,headers=self.headers)
            for content in r.json()['items']:
                # self.repos.append(json.loads(content, object_hook=lambda d: SimpleNamespace(**d)))
                repo_list.append(content['full_name'])
                # print(content['clone_url'])
            idx += len(r.json()['items'])
            print(idx)

        return repo_list

    def search_commits(self, repo):
        SEARCH_COMMIT='search/commits'
        COMMIT_QUERY=f'q=repo:{repo}+perf'
        OPTIONS='&sort=committer-date&order=desc&per_page=100&page=5'
        TARGET=self.API_root+'/'+SEARCH_COMMIT+'?'+COMMIT_QUERY+OPTIONS
        keywords = [
            'perf',
            'reduce allocation',
            'performance',
        ]

        count=0
        max_commit = 100
        while(count < max_commit):
            r = requests.get(TARGET,headers=self.headers)
            if r.status_code != 200:
                break
            if count == 0:
                print(f'{repo} has', r.json()['total_count'], 'commits')
                max_commit = min(r.json()['total_count'],500)
                if max_commit == 0:
                    break
            idx = 1
            start = False
            for content in r.json()['items']:
                msg = content['commit']['message']
                # flag = False
                # for keyword in keywords:
                #     flag = flag or keyword in msg
                # if flag == False:
                #     continue

                if idx == 1:
                    start = True
                    print(f'START {repo}')

                print(f'commit{idx}', msg)
                idx += 1

            if start == True:
                print(f'END {repo}\n')
            count += len(r.json()['items'])

pygithub = PyGithub()
repo_list = pygithub.search_repo()
for repo in repo_list:
    try:
        pygithub.search_commits(repo)
    except:
        # print(f'{repo} has no commits')
        pass