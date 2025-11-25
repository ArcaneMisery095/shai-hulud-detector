from github import Github, GithubException
from typing import List, Tuple, Optional

PATTERNS = [
    "Sha1-Hulud: The Second Coming.",
    # Add more patterns here if needed
]

def scan_user(github: Github, username: str, patterns: Optional[List[str]] = None) -> Tuple[str, str, Optional[str]]:
    """Scan a user. Returns (status, username, info)"""
    patterns = patterns or PATTERNS
    try:
        user = github.get_user(username)
        for repo in user.get_repos():
            if repo.description:
                for p in patterns:
                    if p in repo.description:
                        return ("FLAG", username, repo.html_url)
        return ("OKAY", username, None)
    except GithubException as e:
        return ("ERROR", username, str(e.data if hasattr(e, "data") else e))
    except Exception as e:
        return ("ERROR", username, str(e))

def get_org_members(github: Github, org_name: str) -> List[str]:
    """Return list of logins for all members in an org."""
    org = github.get_organization(org_name)
    return [member.login for member in org.get_members()]