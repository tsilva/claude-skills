#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Repository discovery utilities.

Provides functions for finding git repositories in a directory.
"""

import argparse
import sys
from pathlib import Path


def find_repos(repos_dir: Path) -> list[Path]:
    """
    Find all git repositories in directory.

    Args:
        repos_dir: Directory to search for repositories

    Returns:
        List of paths to repositories, sorted by name (case-insensitive)
    """
    repos = []
    repos_dir = Path(repos_dir).resolve()

    if not repos_dir.exists():
        return repos

    for item in repos_dir.iterdir():
        if item.is_dir() and (item / ".git").exists():
            repos.append(item)

    return sorted(repos, key=lambda p: p.name.lower())


def run_tests() -> bool:
    """Self-test the repo discovery logic."""
    import tempfile

    all_passed = True

    # Test 1: Empty directory returns empty list
    with tempfile.TemporaryDirectory() as tmpdir:
        repos = find_repos(Path(tmpdir))
        if repos != []:
            print(f"FAIL: Empty dir should return empty list, got {repos}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Empty directory")

    # Test 2: Non-existent directory returns empty list
    repos = find_repos(Path("/nonexistent/path/that/does/not/exist"))
    if repos != []:
        print(f"FAIL: Non-existent dir should return empty list, got {repos}", file=sys.stderr)
        all_passed = False
    else:
        print("PASS: Non-existent directory")

    # Test 3: Finds git repos
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create a git repo
        repo1 = tmpdir / "repo-alpha"
        repo1.mkdir()
        (repo1 / ".git").mkdir()

        # Create another git repo
        repo2 = tmpdir / "repo-beta"
        repo2.mkdir()
        (repo2 / ".git").mkdir()

        # Create a non-repo directory
        non_repo = tmpdir / "not-a-repo"
        non_repo.mkdir()

        repos = find_repos(tmpdir)
        repo_names = [r.name for r in repos]

        if repo_names != ["repo-alpha", "repo-beta"]:
            print(f"FAIL: Expected ['repo-alpha', 'repo-beta'], got {repo_names}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Finds git repos")

    # Test 4: Case-insensitive sorting
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        for name in ["Zebra", "alpha", "BETA"]:
            repo = tmpdir / name
            repo.mkdir()
            (repo / ".git").mkdir()

        repos = find_repos(tmpdir)
        repo_names = [r.name for r in repos]

        if repo_names != ["alpha", "BETA", "Zebra"]:
            print(f"FAIL: Expected case-insensitive sort ['alpha', 'BETA', 'Zebra'], got {repo_names}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Case-insensitive sorting")

    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="Find git repositories in a directory"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Directory to search (default: current directory)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run self-tests",
    )

    args = parser.parse_args()

    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    repos = find_repos(args.path)

    if not repos:
        print(f"No repositories found in {args.path}", file=sys.stderr)
        sys.exit(1)

    for repo in repos:
        print(repo)


if __name__ == "__main__":
    main()
