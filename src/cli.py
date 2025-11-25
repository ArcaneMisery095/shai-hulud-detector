import typer
from typing import List, Optional
import concurrent.futures

from src.github_utils import get_github_client
from src.scanner import scan_user, get_org_members

app = typer.Typer()

@app.command()
def scan(
    usernames: List[str] = typer.Argument(None, help="GitHub usernames to scan"),
    org: Optional[str] = typer.Option(None, "--org", "-o", help="GitHub org to scan all members"),
    token: Optional[str] = typer.Option(None, "--token", "-t", help="GitHub token (or set GITHUB_TOKEN)"),
    workers: int = typer.Option(5, "--workers", "-w", help="Concurrent workers"),
):
    """
    Scan GitHub user(s) or org members for shai-hulud compromise.
    """
    github = get_github_client(token)

    if org:
        try:
            scan_list = get_org_members(github, org)
            typer.echo(f"Scanning {len(scan_list)} org members in {org} ...")
        except Exception as e:
            typer.secho(f"Error getting org members: {e}", fg=typer.colors.YELLOW, err=True)
            raise typer.Exit(1)
    elif usernames:
        scan_list = usernames
    else:
        typer.secho("Error: Provide usernames or --org", fg=typer.colors.YELLOW, err=True)
        raise typer.Exit(1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(scan_user, github, u): u for u in scan_list}
        for future in concurrent.futures.as_completed(futures):
            status, username, info = future.result()
            if status == "FLAG":
                typer.secho(f"[FLAG] {username} compromised: {info}", fg=typer.colors.RED)
            elif status == "OKAY":
                typer.secho(f"[OKAY] {username}", fg=typer.colors.GREEN)
            else:
                typer.secho(f"[ERROR] {username}: {info}", fg=typer.colors.YELLOW)

def main():
    app()