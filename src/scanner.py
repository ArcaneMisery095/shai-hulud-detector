from github import Github, GithubException
from typing import List, Tuple, Optional, Callable

PATTERNS = [
    "Sha1-Hulud: The Second Coming.",
    # Add more patterns here if needed
]

def scan_user(
    github: Github, 
    username: str, 
    patterns: Optional[List[str]] = None, 
    verbose_callback: Optional[Callable[[str], None]] = None
) -> Tuple[str, str, Optional[str], dict]:
    """Scan a user. Returns (status, username, info, stats) where stats contains repo_count"""
    patterns = patterns or PATTERNS
    stats = {"repo_count": 0, "repos_with_description": 0}
    
    def log(msg: str):
        if verbose_callback:
            verbose_callback(msg)
    
    try:
        log(f"Starting scan for user: {username}")
        
        user = github.get_user(username)
        repos = list(user.get_repos())
        stats["repo_count"] = len(repos)
        
        log(f"Found {stats['repo_count']} repositories for {username}")
        
        for repo in repos:
            if repo.description:
                stats["repos_with_description"] += 1
                log(f"  Checking repo: {repo.name} (description: {repo.description[:50]}...)")
                
                for p in patterns:
                    if p in repo.description:
                        log(f"  ⚠️  Pattern match found in {repo.name}: {p}")
                        return ("FLAG", username, repo.html_url, stats)
        
        log(f"Scan complete for {username}: {stats['repo_count']} repos, {stats['repos_with_description']} with descriptions, no matches found")
        
        return ("OKAY", username, None, stats)
    except GithubException as e:
        error_msg = str(e.data if hasattr(e, "data") else e)
        log(f"GitHub API error for {username}: {error_msg}")
        return ("ERROR", username, error_msg, stats)
    except Exception as e:
        error_msg = str(e)
        log(f"Unexpected error for {username}: {error_msg}")
        return ("ERROR", username, error_msg, stats)

def get_org_members(github: Github, org_name: str) -> List[str]:
    """Return list of logins for all members in an org."""
    org = github.get_organization(org_name)
    return [member.login for member in org.get_members()]