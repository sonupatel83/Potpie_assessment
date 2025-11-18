import requests
from ..config import Config
from ..logger import logging


def fetch_pr_files(repo_url: str, pr_number: int):
    """Fetch files changed in a PR"""
    try:
        if not repo_url.startswith("https://github.com/"):
            raise ValueError("Invalid GitHub repository URL.")

        parts = repo_url.rstrip("/").split("/")
        if len(parts) < 2:
            raise ValueError("Invalid GitHub repository URL structure.")

        owner, repo = parts[-2], parts[-1]
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if Config.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {Config.GITHUB_TOKEN}"

        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            raise Exception(f"Pull Request #{pr_number} not found for repository {owner}/{repo}.")
        elif response.status_code != 200:
            raise Exception(f"GitHub API Error: {response.status_code} - {response.text}")

        return [
            {"filename": file["filename"], "content": file.get("patch", "")}
            for file in response.json()
        ]
        
    except ValueError as ve:
        logging.error(f"GitHub API Request Error: {ve}")
        raise Exception(f"URL Parsing Error: {ve}")
    except Exception as e:
        logging.error(f"GitHub API Request Error: {e}")
        raise Exception(f"GitHub Fetch Error: {e}")


def fetch_pr_commits(repo_url: str, pr_number: int, limit: int = 2):
    """Fetch commits from a PR (default: 2 commits)"""
    try:
        if not repo_url.startswith("https://github.com/"):
            raise ValueError("Invalid GitHub repository URL.")

        parts = repo_url.rstrip("/").split("/")
        if len(parts) < 2:
            raise ValueError("Invalid GitHub repository URL structure.")

        owner, repo = parts[-2], parts[-1]
        
        # First, get PR info to get the commits URL
        pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if Config.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {Config.GITHUB_TOKEN}"

        pr_response = requests.get(pr_url, headers=headers)
        if pr_response.status_code != 200:
            raise Exception(f"GitHub API Error: {pr_response.status_code} - {pr_response.text}")
        
        pr_data = pr_response.json()
        commits_url = pr_data.get("commits_url", f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits")
        
        # Fetch commits
        commits_response = requests.get(commits_url, headers=headers, params={"per_page": limit})
        if commits_response.status_code != 200:
            raise Exception(f"GitHub API Error: {commits_response.status_code} - {commits_response.text}")
        
        commits = commits_response.json()[:limit]  # Limit to requested number
        
        # Fetch details for each commit
        commit_details = []
        for commit in commits:
            commit_sha = commit.get("sha", "")
            commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
            commit_detail_response = requests.get(commit_url, headers=headers)
            
            if commit_detail_response.status_code == 200:
                commit_data = commit_detail_response.json()
                commit_details.append({
                    "sha": commit_sha[:7],  # Short SHA
                    "message": commit.get("commit", {}).get("message", ""),
                    "author": commit.get("commit", {}).get("author", {}).get("name", ""),
                    "date": commit.get("commit", {}).get("author", {}).get("date", ""),
                    "files": [
                        {
                            "filename": file.get("filename", ""),
                            "status": file.get("status", ""),
                            "additions": file.get("additions", 0),
                            "deletions": file.get("deletions", 0),
                            "patch": file.get("patch", "")
                        }
                        for file in commit_data.get("files", [])
                    ]
                })
        
        return commit_details
        
    except ValueError as ve:
        logging.error(f"GitHub API Request Error: {ve}")
        raise Exception(f"URL Parsing Error: {ve}")
    except Exception as e:
        logging.error(f"GitHub API Request Error: {e}")
        raise Exception(f"GitHub Fetch Error: {e}")

# import requests
# from ..config import Config

# def fetch_pr_files(repo_url: str, pr_number: int):
#     try:
#         # Extract owner and repo name from the URL
#         if not repo_url.startswith("https://github.com/"):
#             raise ValueError("Invalid GitHub repository URL.")
        
#         parts = repo_url.rstrip("/").split("/")
#         if len(parts) < 2:
#             raise ValueError("Invalid GitHub repository URL structure.")
        
#         owner, repo = parts[-2], parts[-1]

#         # Construct the API URL
#         url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
#         headers = {
#             "Accept": "application/vnd.github.v3+json",
#             "Authorization": f"Bearer {Config.GITHUB_TOKEN}",
#         }

#         response = requests.get(url, headers=headers)
#         if response.status_code == 404:
#             raise Exception(f"Pull Request #{pr_number} not found for repository {owner}/{repo}.")
#         elif response.status_code != 200:
#             raise Exception(f"GitHub API Error: {response.status_code} - {response.text}")

#         # Return list of files with content
#         return [
#             {"filename": file["filename"], "content": file.get("patch", "")}
#             for file in response.json()
#         ]
#     except ValueError as ve:
#         raise Exception(f"URL Parsing Error: {ve}")
#     except Exception as e:
#         raise Exception(f"GitHub Fetch Error: {e}")


 