"""
Downloads folders from github repo
Requires PyGithub
pip install PyGithub
pip install gitpython
pip install pygithub3
install git

Purpose: clone the git repository with latest release of branch provided in command line argument

To run this script send command line argument as below change as per your requirement
Make sure destination folder is present and its empty each time before you run this.
python git_clone_latest_release.py --token="" --repository='https://github.com/bibhutibhusanpanda67/master' --branch='master' --destination_folder='C:/Users/bbhushan/Desktop/gitdownload/git_downloads'
"""

import os
import stat
import sys
import base64
import shutil
import getopt
from github import Github
from github import GithubException

import time
import git
from git import RemoteProgress
import subprocess
import gc



def change_permissions_recursive(path, mode):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in [os.path.join(root,d) for d in dirs]:
            os.chmod(dir, mode)
    for file in [os.path.join(root, f) for f in files]:
            os.chmod(file, mode)

def is_empty(path):
    if os.path.exists(path):
  
        # Checking if the directory is empty or not
        if not os.listdir(path):
            print("Empty directory")
            return 'EMPTY_DIR'
        else:
            print("Not empty directory")
            return 'NOT_EMPTY'
    else:
        print("The path does not exist")
        return 'INVALID_DIR'

class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            print(message)

def branch_exist(destination_folder,branch):
    #get list of branches
    repo = git.Repo(destination_folder)
    remote_refs = repo.remote().refs
    
    branches = []
    
    for refs in remote_refs:
        print(refs.name)
        branches.append(refs.name[7:]) #got the available branches to the list
        print("available branches:\n",branches)

    #get current branch
    repo_heads = repo.heads # or it's alias: r.branches

    repo_heads_names = [h.name for h in repo_heads]

    print("current branch:",repo_heads_names)
    
    for b in branches:
        if(b == branch):
            return True
            
    return False

def clone_update_latest(repository, destination_folder, branch):
    empty = is_empty(destination_folder)
    """
    TODO: File system handeling
    repo=git.Repo.init(destination_folder)
    gc.collect()
    repo.git.clear_cache()
    print(empty)
   
    if empty == 'INVALID_DIR':
        os.makedirs(destination_folder)
    if empty == 'NOT_EMPTY':
        shutil.rmtree(destination_folder)
    """
    
    print('Cloning into %s ' % destination_folder)
    repo=git.Repo.clone_from(repository, destination_folder, branch=branch, progress=CloneProgress() )
    
    if branch:
        if branch_exist(destination_folder,branch):
            repo.git.checkout(branch)

    #tags = repo.tags
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)

    print(tags[-1])
    tag = tags[-1]
    if tag:
        repo.git.checkout(tag)
    
    repo.remote().fetch()

    tag_id = -1 # Return the position of an existing tag in my_repo.tags
    repo.head.reference = repo.tags[tag_id]
    repo.head.reset(index=True, working_tree=True)
    fetch_info = repo.remotes.origin.fetch('master:master') #need to get current branch and new branch as variable
    for info in fetch_info:
        print('{} {} {}'.format(info.ref, info.old_commit, info.flags))
    
def login(token):
    github = Github(token)
    user = github.get_user()
    print(user)
    login = user.login
    print(login)

def usage():
    """
    Prints the usage command lines
    token,org can be None
    """
    print ("usage: gh-download --token=None --repository=repository --branch='master' --destination_folder=folder")
    
def main(argv):
    """
    Main function block
    """
    token = None
    tag = None
    branch = ''
    repository = ''
    destination_folder = ''
    
    try:
        opts, args = getopt.getopt(argv, "t:o:r:b:f:", ["token=", "repository=", "branch=", "destination_folder="])
        print(opts)
    except getopt.GetoptError as err:
        print("error to get opts:", str(err))
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-t", "--token"):
            token = arg
        elif opt in ("-r", "--repository"):
            repository = arg
        elif opt in ("-b", "--branch"):
            branch = arg
        elif opt in ("-f", "--destination_folder"):
            destination_folder = arg
            
    print("token:",token)
    print("repository:",repository)
    print("branch:",branch)
    print("destination_folder:",destination_folder)
    
    
    clone_update_latest(repository,destination_folder,branch)
    

if __name__ == "__main__":
    """
    Entry point
    """
    main(sys.argv[1:])
