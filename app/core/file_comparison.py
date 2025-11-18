"""
File comparison utilities for comparing files from different repositories
"""
import requests
import difflib
import time
from typing import Dict, Any, Optional
from ..config import Config
from ..logger import logging


def fetch_file_from_raw_url(raw_url: str, ref: str = "HEAD") -> Dict[str, Any]:
    """
    Fetch a file from a GitHub raw URL and return content with metadata
    """
    result = {
        "raw_url": raw_url,
        "fetched": False,
        "content": None,
        "meta": {
            "ref": ref,
            "size": 0,
            "sha": None,
            "last_commit_msg": None
        },
        "error": None
    }
    
    try:
        # Fetch the file content
        headers = {}
        if Config.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {Config.GITHUB_TOKEN}"
        
        response = requests.get(raw_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
            return result
        
        content = response.text
        result["content"] = content
        result["meta"]["size"] = len(content.encode('utf-8'))
        result["fetched"] = True
        
        # Try to extract commit info from URL
        # Convert raw URL to API URL to get commit info
        try:
            # raw URL format: https://raw.githubusercontent.com/owner/repo/branch/path
            # API URL format: https://api.github.com/repos/owner/repo/contents/path?ref=branch
            parts = raw_url.replace("https://raw.githubusercontent.com/", "").split("/")
            if len(parts) >= 4:
                owner = parts[0]
                repo = parts[1]
                branch = parts[2]
                file_path = "/".join(parts[3:])
                
                api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
                api_params = {"ref": branch}
                
                api_response = requests.get(api_url, headers=headers, params=api_params, timeout=10)
                if api_response.status_code == 200:
                    api_data = api_response.json()
                    result["meta"]["sha"] = api_data.get("sha", None)
                    
                    # Try to get last commit message
                    commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
                    commits_params = {"path": file_path, "per_page": 1}
                    commits_response = requests.get(commits_url, headers=headers, params=commits_params, timeout=10)
                    if commits_response.status_code == 200:
                        commits = commits_response.json()
                        if commits:
                            result["meta"]["last_commit_msg"] = commits[0].get("commit", {}).get("message", "").split("\n")[0]
        except Exception as e:
            logging.warning(f"Could not fetch metadata for {raw_url}: {e}")
            # Continue without metadata
        
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)
        logging.error(f"Error fetching file {raw_url}: {e}")
    except Exception as e:
        result["error"] = str(e)
        logging.error(f"Unexpected error fetching file {raw_url}: {e}")
    
    return result


def compute_unified_diff(file_a_content: str, file_b_content: str, file_a_name: str = "file_a", file_b_name: str = "file_b") -> Dict[str, Any]:
    """
    Compute unified diff between two files
    """
    lines_a = file_a_content.splitlines(keepends=True)
    lines_b = file_b_content.splitlines(keepends=True)
    
    diff = list(difflib.unified_diff(
        lines_a, lines_b,
        fromfile=file_a_name,
        tofile=file_b_name,
        lineterm=''
    ))
    
    unified_diff_text = ''.join(diff)
    
    # Count changes
    added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
    removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
    modified = min(added, removed)  # Approximate
    
    # Truncate if too long
    max_diff_length = 20000
    if len(unified_diff_text) > max_diff_length:
        unified_diff_text = unified_diff_text[:max_diff_length] + "\n... (truncated)"
    
    return {
        "unified_diff": unified_diff_text,
        "summary_lines_changed": {
            "added": added,
            "removed": removed,
            "modified": modified
        }
    }

