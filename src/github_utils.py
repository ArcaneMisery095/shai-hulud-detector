import os
from github import Github

def get_github_client(token: str = None):
    """Return authenticated or anonymous Github client."""
    token = token or os.environ.get("GITHUB_TOKEN")
    return Github(token) if token else Github()