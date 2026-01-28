#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Fix Claude sandbox settings for repositories.

Creates .claude/settings.local.json with sandbox.enabled: true for repos
that don't have it configured.

Usage:
    uv run scripts/fix_sandbox.py --repos-dir /path/to/repos
    uv run scripts/fix_sandbox.py --repos-dir /path/to/repos --dry-run
    uv run scripts/fix_sandbox.py --repos-dir /path/to/repos --filter "prefix"

Output:
    JSON report to stdout with created/skipped per repo
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Import shared utilities
SCRIPT_DIR = Path(__file__).parent
SHARED_DIR = SCRIPT_DIR.parent.parent.parent.parent.parent / "shared"
sys.path.insert(0, str(SHARED_DIR))
from repo_utils import find_repos

SANDBOX_SETTINGS = {
    "sandbox": {
        "enabled": True
    },
    "permissions": {
        "allow": [],
        "deny": []
    }
}


def has_sandbox_enabled(repo_path: Path) -> bool:
    """Check if repo already has sandbox.enabled: true."""
    claude_dir = repo_path / ".claude"
    settings_files = [
        claude_dir / "settings.json",
        claude_dir / "settings.local.json",
    ]

    for settings_file in settings_files:
        if settings_file.exists():
            try:
                content = settings_file.read_text(encoding="utf-8", errors="ignore")
                data = json.loads(content)
                if isinstance(data.get("sandbox"), dict) and data["sandbox"].get("enabled") is True:
                    return True
            except (json.JSONDecodeError, Exception):
                pass

    return False


def create_sandbox_settings(repo_path: Path, dry_run: bool = False) -> dict:
    """Create sandbox settings for a repo."""
    claude_dir = repo_path / ".claude"
    settings_file = claude_dir / "settings.local.json"

    result = {
        "repo": repo_path.name,
        "settings_path": str(settings_file),
    }

    # Check if already configured
    if has_sandbox_enabled(repo_path):
        result["status"] = "skipped"
        result["reason"] = "sandbox already enabled"
        return result

    if dry_run:
        result["status"] = "would_create"
        result["content"] = SANDBOX_SETTINGS
        return result

    try:
        # Create .claude directory if needed
        claude_dir.mkdir(parents=True, exist_ok=True)

        # Check if settings.local.json exists and merge
        existing_settings = {}
        if settings_file.exists():
            try:
                existing_settings = json.loads(settings_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, Exception):
                pass

        # Merge: add sandbox.enabled, preserve existing permissions
        merged = existing_settings.copy()
        merged["sandbox"] = {"enabled": True}
        if "permissions" not in merged:
            merged["permissions"] = {"allow": [], "deny": []}

        # Write the file
        settings_file.write_text(
            json.dumps(merged, indent=2) + "\n",
            encoding="utf-8"
        )

        result["status"] = "created"
        result["content"] = merged

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Fix Claude sandbox settings for repositories"
    )
    parser.add_argument(
        "--repos-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory containing repos (default: current directory)",
    )
    parser.add_argument(
        "--filter",
        type=str,
        help="Filter repos by name substring",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    # Find repos
    repos = find_repos(args.repos_dir)

    if args.filter:
        repos = [r for r in repos if args.filter.lower() in r.name.lower()]

    if not repos:
        print(json.dumps({
            "error": "No repositories found",
            "repos_dir": str(args.repos_dir),
            "filter": args.filter,
        }, indent=2))
        sys.exit(1)

    # Process repos
    results = []
    for repo in repos:
        result = create_sandbox_settings(repo, dry_run=args.dry_run)
        results.append(result)

    # Summary
    created = sum(1 for r in results if r["status"] in ("created", "would_create"))
    skipped = sum(1 for r in results if r["status"] == "skipped")
    errors = sum(1 for r in results if r["status"] == "error")

    report = {
        "timestamp": datetime.now().isoformat(),
        "repos_dir": str(args.repos_dir),
        "filter": args.filter,
        "dry_run": args.dry_run,
        "summary": {
            "total": len(results),
            "created": created,
            "skipped": skipped,
            "errors": errors,
        },
        "results": results,
    }

    print(json.dumps(report, indent=2))

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
