import requests
from ..config import Config
#from app.Settings import Settings

class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {"Authorization": f"token {Config.GITHUB_TOKEN}"}

    def get_user_repos(self, username):
        url = f"{self.base_url}/users/{username}/repos"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
