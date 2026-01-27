#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Sync GitHub repository descriptions from README taglines.

Extracts taglines from README.md files and updates GitHub repo descriptions
using the gh CLI.

Usage:
    uv run scripts/sync_descriptions.py --repos-dir /path/to/repos
    uv run scripts/sync_descriptions.py --repos-dir /path/to/repos --dry-run
    uv run scripts/sync_descriptions.py --repos-dir /path/to/repos --filter "sandbox"

Output:
    JSON report to stdout with success/failure per repo
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Import extract_tagline from same directory
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from extract_tagline import extract_tagline


def find_repos(repos_dir: Path) -> list[Path]:
    """Find all git repositories in directory."""
    repos = []
    repos_dir = Path(repos_dir).resolve()

    if not repos_dir.exists():
        return repos

    for item in repos_dir.iterdir():
        if item.is_dir() and (item / ".git").exists():
            repos.append(item)

    return sorted(repos, key=lambda p: p.name.lower())


def check_gh_cli() -> bool:
    """Check if gh CLI is available and authenticated."""
    if not shutil.which("gh"):
        return False

    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_github_description(repo_path: Path) -> str | None:
    """Get current GitHub description for a repo."""
    try:
        result = subprocess.run(
            ["gh", "repo", "view", repo_path.name, "--json", "description"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(repo_path),
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("description", "") or ""
    except Exception:
        pass
    return None


def set_github_description(repo_path: Path, description: str, dry_run: bool = False) -> tuple[bool, str]:
    """
    Set GitHub description for a repo.

    Returns:
        (success, message) tuple
    """
    if dry_run:
        return True, f"[DRY RUN] Would set description: {description}"

    try:
        result = subprocess.run(
            ["gh", "repo", "edit", "--description", description],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(repo_path),
        )

        if result.returncode == 0:
            return True, "Description updated"
        else:
            return False, f"gh error: {result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return False, "Timeout executing gh command"
    except Exception as e:
        return False, f"Error: {e}"


def sync_repo(repo_path: Path, dry_run: bool = False) -> dict:
    """
    Sync description for a single repo.

    Returns:
        Result dict with status and details
    """
    repo_name = repo_path.name
    readme_path = repo_path / "README.md"

    result = {
        "repo": repo_name,
        "path": str(repo_path),
        "status": "unknown",
        "tagline": None,
        "current_description": None,
        "message": None,
    }

    # Check README exists
    if not readme_path.exists():
        result["status"] = "skipped"
        result["message"] = "No README.md found"
        return result

    # Extract tagline
    tagline = extract_tagline(readme_path)
    if not tagline:
        result["status"] = "skipped"
        result["message"] = "Could not extract tagline from README"
        return result

    result["tagline"] = tagline

    # Get current description
    current = get_github_description(repo_path)
    if current is None:
        result["status"] = "skipped"
        result["message"] = "Could not fetch GitHub description (not a GitHub repo?)"
        return result

    result["current_description"] = current

    # Check if already synced
    if current.strip().lower() == tagline.strip().lower():
        result["status"] = "synced"
        result["message"] = "Already in sync"
        return result

    # Update description
    success, message = set_github_description(repo_path, tagline, dry_run)

    if success:
        result["status"] = "updated" if not dry_run else "would_update"
        result["message"] = message
    else:
        result["status"] = "failed"
        result["message"] = message

    return result


def sync_all(repos_dir: Path, repo_filter: str | None = None, dry_run: bool = False) -> dict:
    """
    Sync descriptions for all repos in directory.

    Returns:
        Report dict with results for each repo
    """
    repos_dir = Path(repos_dir).resolve()

    # Check gh CLI
    if not check_gh_cli():
        return {
            "error": "gh CLI not available or not authenticated (run: gh auth login)",
            "repos_dir": str(repos_dir),
        }

    # Find repos
    repos = find_repos(repos_dir)

    if repo_filter:
        repos = [r for r in repos if repo_filter.lower() in r.name.lower()]

    if not repos:
        return {
            "error": f"No repositories found in {repos_dir}" + (f" matching '{repo_filter}'" if repo_filter else ""),
            "repos_dir": str(repos_dir),
        }

    # Sync each repo
    results = []
    for repo in repos:
        results.append(sync_repo(repo, dry_run))

    # Summarize
    summary = {
        "total": len(results),
        "updated": sum(1 for r in results if r["status"] == "updated"),
        "would_update": sum(1 for r in results if r["status"] == "would_update"),
        "synced": sum(1 for r in results if r["status"] == "synced"),
        "skipped": sum(1 for r in results if r["status"] == "skipped"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
    }

    return {
        "sync_time": datetime.now().isoformat(),
        "repos_dir": str(repos_dir),
        "dry_run": dry_run,
        "repos": results,
        "summary": summary,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Sync GitHub repository descriptions from README taglines"
    )
    parser.add_argument(
        "--repos-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory containing repositories (default: current directory)",
    )
    parser.add_argument(
        "--filter",
        type=str,
        help="Filter repos by name (partial match)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full JSON report (default: summary only)",
    )

    args = parser.parse_args()

    # Run sync
    report = sync_all(args.repos_dir, args.filter, args.dry_run)

    # Handle errors
    if "error" in report:
        print(f"Error: {report['error']}", file=sys.stderr)
        if args.json:
            print(json.dumps(report, indent=2))
        sys.exit(1)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        # Human-readable output
        print(f"Description Sync Report")
        print(f"=======================")
        print(f"Directory: {report['repos_dir']}")
        print(f"Dry run: {report['dry_run']}")
        print()

        summary = report["summary"]
        if args.dry_run:
            print(f"Would update: {summary['would_update']}")
        else:
            print(f"Updated: {summary['updated']}")
        print(f"Already synced: {summary['synced']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Failed: {summary['failed']}")
        print()

        # Show details for non-synced repos
        for result in report["repos"]:
            if result["status"] in ("updated", "would_update"):
                print(f"✓ {result['repo']}")
                print(f"  Tagline: {result['tagline']}")
                if result["current_description"]:
                    print(f"  Was: {result['current_description']}")
                print()
            elif result["status"] == "failed":
                print(f"✗ {result['repo']}: {result['message']}")
                print()

    # Exit code based on failures
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
