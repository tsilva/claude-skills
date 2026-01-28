#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///
"""
Auto-apply trivial fixes from audit report without LLM intervention.

Usage:
    uv run apply_safe_fixes.py --audit-report <path> [--dry-run] [--repo <name>]

Safe fixes (auto-applicable):
    - GITIGNORE_EXISTS: Copy template gitignore
    - LICENSE_EXISTS: Copy MIT license template
    - CLAUDE_MD_EXISTS: Create minimal CLAUDE.md

Unsafe fixes (returned for Claude to handle):
    - README_EXISTS: Requires content generation
    - LOGO_EXISTS: Requires image generation
    - README_HAS_TAGLINE: Requires creative writing
    - README_CURRENT: Requires content analysis
    - DESCRIPTION_SYNCED: Requires API call + verification
    - PII_CLEAN: Requires manual review

Output:
    JSON: {"applied": [...], "remaining": [...], "errors": [...]}
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = SCRIPT_DIR.parent / "assets" if (SCRIPT_DIR.parent / "assets").exists() else SCRIPT_DIR / "assets"

# Safe checks that can be auto-fixed without LLM
SAFE_CHECKS = {
    "GITIGNORE_EXISTS",
    "LICENSE_EXISTS",
    "CLAUDE_MD_EXISTS",
    "CLAUDE_SETTINGS_SANDBOX",
}

# Checks that require LLM intervention
UNSAFE_CHECKS = {
    "README_EXISTS",
    "README_CURRENT",
    "README_HAS_LICENSE",
    "LOGO_EXISTS",
    "DESCRIPTION_SYNCED",
    "PII_CLEAN",
    "GITIGNORE_COMPLETE",
    "PYTHON_PYPROJECT",
    "PYTHON_UV_INSTALL",
}


def fix_gitignore_exists(repo_path: Path, dry_run: bool) -> Tuple[bool, str]:
    """Copy gitignore template to repo."""
    target = repo_path / ".gitignore"
    template = ASSETS_DIR / "gitignore-template.txt"

    if target.exists():
        return True, "Already exists"

    if not template.exists():
        return False, f"Template not found: {template}"

    if dry_run:
        return True, f"Would create {target}"

    try:
        shutil.copy(template, target)
        return True, f"Created {target}"
    except Exception as e:
        return False, f"Failed to create .gitignore: {e}"


def fix_license_exists(repo_path: Path, dry_run: bool) -> Tuple[bool, str]:
    """Copy MIT license template to repo."""
    target = repo_path / "LICENSE"
    template = ASSETS_DIR / "LICENSE"

    # Check if any license exists
    for name in ["LICENSE", "LICENSE.md", "LICENSE.txt"]:
        if (repo_path / name).exists():
            return True, f"License already exists at {name}"

    if not template.exists():
        return False, f"Template not found: {template}"

    if dry_run:
        return True, f"Would create {target}"

    try:
        # Read template and substitute placeholders
        content = template.read_text()
        year = str(datetime.now().year)

        # Try to get author from git config
        author = "Author"
        try:
            import subprocess
            result = subprocess.run(
                ["git", "-C", str(repo_path), "config", "user.name"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                author = result.stdout.strip()
        except Exception:
            pass

        content = content.replace("[year]", year)
        content = content.replace("[fullname]", author)

        target.write_text(content)
        return True, f"Created {target} (MIT License, {year}, {author})"
    except Exception as e:
        return False, f"Failed to create LICENSE: {e}"


def fix_claude_md_exists(repo_path: Path, dry_run: bool) -> Tuple[bool, str]:
    """Create minimal CLAUDE.md file."""
    target = repo_path / "CLAUDE.md"

    if target.exists():
        return True, "Already exists"

    if dry_run:
        return True, f"Would create {target}"

    # Get project name from directory
    project_name = repo_path.name

    content = f"""# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project: {project_name}

*Add project-specific instructions here.*
"""

    try:
        target.write_text(content)
        return True, f"Created minimal {target}"
    except Exception as e:
        return False, f"Failed to create CLAUDE.md: {e}"


def fix_claude_settings_sandbox(repo_path: Path, dry_run: bool) -> Tuple[bool, str]:
    """Create or update .claude/settings.json with sandbox enabled."""
    claude_dir = repo_path / ".claude"
    settings_path = claude_dir / "settings.json"

    if dry_run:
        if settings_path.exists():
            return True, f"Would update {settings_path} with sandbox.enabled: true"
        return True, f"Would create {settings_path} with sandbox.enabled: true"

    try:
        # Create .claude directory if needed
        claude_dir.mkdir(exist_ok=True)

        # Load existing settings or create new
        if settings_path.exists():
            try:
                existing = json.loads(settings_path.read_text())
            except json.JSONDecodeError:
                existing = {}
        else:
            existing = {}

        # Ensure sandbox.enabled is set
        if "sandbox" not in existing:
            existing["sandbox"] = {}
        existing["sandbox"]["enabled"] = True

        settings_path.write_text(json.dumps(existing, indent=2) + "\n")
        return True, f"Updated {settings_path} with sandbox.enabled: true"
    except Exception as e:
        return False, f"Failed to update settings: {e}"


# Map check names to fix functions
FIX_FUNCTIONS = {
    "GITIGNORE_EXISTS": fix_gitignore_exists,
    "LICENSE_EXISTS": fix_license_exists,
    "CLAUDE_MD_EXISTS": fix_claude_md_exists,
    "CLAUDE_SETTINGS_SANDBOX": fix_claude_settings_sandbox,
}


def apply_fixes(
    audit_report: Dict,
    dry_run: bool = False,
    repo_filter: Optional[str] = None
) -> Dict:
    """
    Apply safe fixes from audit report.

    Args:
        audit_report: Parsed audit JSON report
        dry_run: If True, don't actually make changes
        repo_filter: Optional filter for specific repo

    Returns:
        Result dict with applied, remaining, and errors
    """
    applied = []
    remaining = []
    errors = []

    repos = audit_report.get("repos", [])

    for repo_data in repos:
        repo_name = repo_data.get("repo")
        repo_path = Path(repo_data.get("path", ""))

        # Apply filter if specified
        if repo_filter and repo_filter.lower() not in repo_name.lower():
            continue

        if not repo_path.exists():
            errors.append({
                "repo": repo_name,
                "error": f"Path does not exist: {repo_path}"
            })
            continue

        for check in repo_data.get("checks", []):
            check_name = check.get("check")

            # Skip passed checks
            if check.get("passed") or check.get("skipped"):
                continue

            # Check if this is a safe fix
            if check_name in SAFE_CHECKS and check_name in FIX_FUNCTIONS:
                fix_func = FIX_FUNCTIONS[check_name]
                success, message = fix_func(repo_path, dry_run)

                if success:
                    applied.append({
                        "repo": repo_name,
                        "check": check_name,
                        "message": message,
                        "dry_run": dry_run
                    })
                else:
                    errors.append({
                        "repo": repo_name,
                        "check": check_name,
                        "error": message
                    })

            elif check_name in UNSAFE_CHECKS:
                # Return for Claude to handle
                remaining.append({
                    "repo": repo_name,
                    "check": check_name,
                    "message": check.get("message"),
                    "auto_fix": check.get("auto_fix"),
                })

    return {
        "applied": applied,
        "remaining": remaining,
        "errors": errors,
        "summary": {
            "applied_count": len(applied),
            "remaining_count": len(remaining),
            "error_count": len(errors),
            "dry_run": dry_run
        }
    }


def run_tests() -> bool:
    """Self-test the fix logic."""
    import tempfile

    all_passed = True

    # Test 1: Fix gitignore
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "test-repo"
        repo.mkdir()

        # Create minimal assets dir with template
        assets = repo / "assets"
        assets.mkdir()
        (assets / "gitignore-template.txt").write_text("# Test gitignore\n.env\n")

        # Temporarily override ASSETS_DIR
        global ASSETS_DIR
        old_assets = ASSETS_DIR
        ASSETS_DIR = assets

        success, msg = fix_gitignore_exists(repo, dry_run=False)
        ASSETS_DIR = old_assets

        gitignore = repo / ".gitignore"
        if not success or not gitignore.exists():
            print(f"FAIL: fix_gitignore_exists - {msg}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: fix_gitignore_exists")

    # Test 2: Dry run doesn't create files
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "test-repo"
        repo.mkdir()

        success, msg = fix_claude_md_exists(repo, dry_run=True)
        claude_md = repo / "CLAUDE.md"

        if not success:
            print(f"FAIL: dry_run should succeed - {msg}", file=sys.stderr)
            all_passed = False
        elif claude_md.exists():
            print("FAIL: dry_run should not create files", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: dry_run mode")

    # Test 3: Create CLAUDE.md
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "my-project"
        repo.mkdir()

        success, msg = fix_claude_md_exists(repo, dry_run=False)
        claude_md = repo / "CLAUDE.md"

        if not success or not claude_md.exists():
            print(f"FAIL: fix_claude_md_exists - {msg}", file=sys.stderr)
            all_passed = False
        elif "my-project" not in claude_md.read_text():
            print("FAIL: CLAUDE.md should contain project name", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: fix_claude_md_exists")

    # Test 4: Safe check classification
    if "README_EXISTS" in SAFE_CHECKS:
        print("FAIL: README_EXISTS should be unsafe", file=sys.stderr)
        all_passed = False
    elif "GITIGNORE_EXISTS" not in SAFE_CHECKS:
        print("FAIL: GITIGNORE_EXISTS should be safe", file=sys.stderr)
        all_passed = False
    else:
        print("PASS: Check classification")

    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="Auto-apply safe fixes from audit report"
    )
    parser.add_argument(
        "--audit-report",
        type=Path,
        help="Path to audit report JSON (default: ~/.claude/repo-maintain-audit.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="Filter to specific repository (partial match)",
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

    # Determine report path
    report_path = args.audit_report
    if not report_path:
        report_path = Path.home() / ".claude" / "repo-maintain-audit.json"

    if not report_path.exists():
        print(f"Error: Audit report not found: {report_path}", file=sys.stderr)
        print("Run audit first: uv run audit.py --repos-dir <path>", file=sys.stderr)
        sys.exit(1)

    # Load audit report
    try:
        audit_data = json.loads(report_path.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in audit report: {e}", file=sys.stderr)
        sys.exit(1)

    # Apply fixes
    result = apply_fixes(audit_data, dry_run=args.dry_run, repo_filter=args.repo)

    # Output result
    print(json.dumps(result, indent=2))

    # Return non-zero if there were errors
    if result["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
