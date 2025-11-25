import typer
from typing import List, Optional
import concurrent.futures

from src.github_utils import get_github_client
from src.scanner import scan_user, get_org_members

app = typer.Typer(
    help="""
    Shai Hulud Detector

    A CLI tool to scan GitHub users and organizations for shai-hulud compromise detection.
    """,
    invoke_without_command=True,
    no_args_is_help=True,
)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Welcome to Shai-Hulud — the worm that detects worms.
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

@app.command(no_args_is_help=True)
def scan(
    usernames: List[str] = typer.Argument(None, help="GitHub usernames to scan"),
    org: Optional[str] = typer.Option(None, "--org", "-o", help="GitHub org to scan all members"),
    token: Optional[str] = typer.Option(None, "--token", "-t", help="GitHub token (or set GITHUB_TOKEN)"),
    workers: int = typer.Option(5, "--workers", "-w", help="Concurrent workers"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show verbose output including repo counts"),
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

    def verbose_log(msg: str):
        if verbose:
            typer.echo(f"  {msg}", err=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(scan_user, github, u, None, verbose_log if verbose else None): u for u in scan_list}
        for future in concurrent.futures.as_completed(futures):
            status, username, info, stats = future.result()
            if status == "FLAG":
                typer.secho(f"[FLAG] {username} compromised: {info}. Stats: {stats['repo_count']} repos scanned, {stats['repos_with_description']} with descriptions", fg=typer.colors.RED)
            elif status == "OKAY":
                typer.secho(f"[OKAY] {username} ({stats['repo_count']} repos, {stats['repos_with_description']} with descriptions)", fg=typer.colors.GREEN)
            else:
                typer.secho(f"[ERROR] {username}: {info}. Stats: {stats.get('repo_count', 0)} repos scanned", fg=typer.colors.YELLOW)

def main():
    app()