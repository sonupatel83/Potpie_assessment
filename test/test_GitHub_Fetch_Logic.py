import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .core.github_utils import fetch_pr_files

repo_url = "https://github.com/prathameshpawar17/Generilized_the-_CRUD_Sqlalchemy"
pr_number = 2
#https://github.com/prathameshpawar17/Generilized_the-_CRUD_Sqlalchemy/pull/2#issue-2746118698 

try:
    files = fetch_pr_files(repo_url, pr_number)
    print(f"Fetched files: {files}")
except Exception as e:
    print(f"Error: {e}")
