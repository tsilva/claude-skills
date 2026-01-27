#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Repository audit script for repo-maintain skill.

Performs deterministic checks on repositories in a directory and outputs
JSON report for remediation workflow.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Import modules from same directory
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from pii_scanner import scan_repo as pii_scan_repo
from extract_tagline import extract_tagline


def check_dependencies() -> dict:
    """Check required external dependencies."""
    results = {
        "git": {"available": False, "error": None},
        "gh": {"available": False, "error": None},
    }

    # Check git
    if shutil.which("git"):
        results["git"]["available"] = True
    else:
        results["git"]["error"] = "git not found in PATH"

    # Check gh CLI
    if shutil.which("gh"):
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                results["gh"]["available"] = True
            else:
                results["gh"]["available"] = True  # gh exists but may not be authed
                results["gh"]["error"] = "gh CLI not authenticated (run: gh auth login)"
        except subprocess.TimeoutExpired:
            results["gh"]["error"] = "gh auth status timed out"
        except Exception as e:
            results["gh"]["error"] = str(e)
    else:
        results["gh"]["error"] = "gh CLI not found in PATH (install: brew install gh)"

    return results


def detect_github_user(repos_dir: Path) -> str | None:
    """Detect GitHub username from git remote origin of any repo."""
    for repo_path in find_repos(repos_dir):
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                # Parse GitHub URL formats:
                # git@github.com:user/repo.git
                # https://github.com/user/repo.git
                match = re.search(r"github\.com[:/]([^/]+)/", url)
                if match:
                    return match.group(1)
        except Exception:
            continue
    return None


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


def check_readme_exists(repo_path: Path) -> dict:
    """Check if README.md exists."""
    readme_path = repo_path / "README.md"
    exists = readme_path.exists()
    return {
        "check": "README_EXISTS",
        "passed": exists,
        "path": str(readme_path) if exists else None,
        "message": "README.md exists" if exists else "README.md not found",
        "auto_fix": "project-readme-author create",
    }


def check_readme_current(repo_path: Path) -> dict:
    """
    Check if README appears to be current using staleness heuristics.

    Heuristics:
    - Has recent commit date vs README modification
    - Contains common outdated markers
    - Has broken badge URLs
    """
    readme_path = repo_path / "README.md"

    if not readme_path.exists():
        return {
            "check": "README_CURRENT",
            "passed": False,
            "message": "README.md does not exist",
            "auto_fix": "project-readme-author create",
        }

    issues = []

    try:
        content = readme_path.read_text(encoding="utf-8", errors="ignore")

        # Check for placeholder content
        placeholders = [
            "TODO",
            "FIXME",
            "Coming soon",
            "Work in progress",
            "Under construction",
            "[Insert",
            "Lorem ipsum",
        ]
        for placeholder in placeholders:
            if placeholder.lower() in content.lower():
                issues.append(f"Contains placeholder: '{placeholder}'")

        # Check for very short README
        if len(content.strip()) < 100:
            issues.append("README is very short (<100 chars)")

        # Check for missing sections
        has_installation = any(x in content.lower() for x in ["install", "setup", "getting started"])
        has_usage = any(x in content.lower() for x in ["usage", "example", "how to"])

        if not has_installation and not has_usage:
            issues.append("Missing installation/usage sections")

    except Exception as e:
        issues.append(f"Could not read README: {e}")

    return {
        "check": "README_CURRENT",
        "passed": len(issues) == 0,
        "message": "README appears current" if not issues else "; ".join(issues),
        "issues": issues,
        "auto_fix": "project-readme-author optimize",
    }


def check_logo_exists(repo_path: Path) -> dict:
    """Check if logo exists in standard locations."""
    logo_patterns = [
        "logo.png", "logo.svg", "logo.jpg",
        "assets/logo.png", "assets/logo.svg",
        "images/logo.png", "images/logo.svg",
        ".github/logo.png", ".github/logo.svg",
    ]

    for pattern in logo_patterns:
        logo_path = repo_path / pattern
        if logo_path.exists():
            return {
                "check": "LOGO_EXISTS",
                "passed": True,
                "path": str(logo_path),
                "message": f"Logo found at {pattern}",
            }

    return {
        "check": "LOGO_EXISTS",
        "passed": False,
        "path": None,
        "message": "No logo found in standard locations",
        "auto_fix": "project-logo-author",
    }


def check_gitignore_exists(repo_path: Path) -> dict:
    """Check if .gitignore exists."""
    gitignore_path = repo_path / ".gitignore"
    exists = gitignore_path.exists()
    return {
        "check": "GITIGNORE_EXISTS",
        "passed": exists,
        "path": str(gitignore_path) if exists else None,
        "message": ".gitignore exists" if exists else ".gitignore not found",
        "auto_fix": "create from template",
    }


def check_gitignore_complete(repo_path: Path) -> dict:
    """Check if .gitignore contains essential patterns."""
    gitignore_path = repo_path / ".gitignore"

    # Essential patterns that should be in most gitignores
    essential_patterns = [
        ".env",
        ".DS_Store",
        "node_modules/",
        "__pycache__/",
        "*.pyc",
        ".venv/",
        "venv/",
    ]

    if not gitignore_path.exists():
        return {
            "check": "GITIGNORE_COMPLETE",
            "passed": False,
            "message": ".gitignore does not exist",
            "missing": essential_patterns,
            "auto_fix": "create from template",
        }

    try:
        content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
        content_lower = content.lower()

        missing = []
        for pattern in essential_patterns:
            # Simple check - pattern or its base should be present
            pattern_base = pattern.rstrip("/").rstrip("*").lower()
            if pattern_base not in content_lower:
                missing.append(pattern)

        return {
            "check": "GITIGNORE_COMPLETE",
            "passed": len(missing) == 0,
            "message": "Essential patterns present" if not missing else f"Missing {len(missing)} patterns",
            "missing": missing,
            "auto_fix": "append missing patterns",
        }
    except Exception as e:
        return {
            "check": "GITIGNORE_COMPLETE",
            "passed": False,
            "message": f"Could not read .gitignore: {e}",
            "auto_fix": "create from template",
        }


def check_claude_md_exists(repo_path: Path) -> dict:
    """Check if CLAUDE.md exists."""
    claude_md_path = repo_path / "CLAUDE.md"
    exists = claude_md_path.exists()
    return {
        "check": "CLAUDE_MD_EXISTS",
        "passed": exists,
        "path": str(claude_md_path) if exists else None,
        "message": "CLAUDE.md exists" if exists else "CLAUDE.md not found",
        "auto_fix": "/init",
    }


def check_description_synced(repo_path: Path) -> dict:
    """Check if GitHub description matches README tagline."""
    readme_path = repo_path / "README.md"

    if not readme_path.exists():
        return {
            "check": "DESCRIPTION_SYNCED",
            "passed": False,
            "message": "README.md does not exist",
            "auto_fix": "create README first",
        }

    # Get repo name
    repo_name = repo_path.name

    # Try to get GitHub description
    try:
        result = subprocess.run(
            ["gh", "repo", "view", repo_name, "--json", "description"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(repo_path),
        )

        if result.returncode != 0:
            return {
                "check": "DESCRIPTION_SYNCED",
                "passed": False,
                "message": "Could not fetch GitHub description (not a GitHub repo or not authenticated)",
                "auto_fix": "gh repo edit --description",
            }

        gh_data = json.loads(result.stdout)
        gh_description = gh_data.get("description", "") or ""

    except Exception as e:
        return {
            "check": "DESCRIPTION_SYNCED",
            "passed": False,
            "message": f"Error fetching GitHub description: {e}",
            "auto_fix": "gh repo edit --description",
        }

    # Extract tagline from README using robust extraction
    readme_tagline = extract_tagline(readme_path)

    if not readme_tagline:
        return {
            "check": "DESCRIPTION_SYNCED",
            "passed": False,
            "message": "Could not extract tagline from README",
            "gh_description": gh_description,
            "auto_fix": "add tagline to README",
        }

    # Compare descriptions (case-insensitive)
    synced = gh_description.lower().strip() == readme_tagline.lower().strip()

    return {
        "check": "DESCRIPTION_SYNCED",
        "passed": synced,
        "message": "Description synced" if synced else "GitHub description differs from README tagline",
        "gh_description": gh_description,
        "readme_tagline": readme_tagline[:200],
        "auto_fix": "gh repo edit --description",
    }


def check_pii_clean(repo_path: Path) -> dict:
    """Check for PII/credentials using pii_scanner."""
    try:
        results = pii_scan_repo(repo_path, respect_gitignore=True)

        if "error" in results:
            return {
                "check": "PII_CLEAN",
                "passed": False,
                "message": results["error"],
                "auto_fix": "manual review required",
            }

        has_critical = results["by_severity"]["critical"] > 0
        has_findings = results["total_findings"] > 0

        return {
            "check": "PII_CLEAN",
            "passed": not has_findings,
            "message": f"No credentials found" if not has_findings else f"Found {results['total_findings']} potential credentials ({results['by_severity']['critical']} critical)",
            "findings_count": results["total_findings"],
            "by_severity": results["by_severity"],
            "files_with_findings": list(results["findings"].keys())[:10],  # Limit to 10
            "auto_fix": "manual review required",
        }

    except Exception as e:
        return {
            "check": "PII_CLEAN",
            "passed": False,
            "message": f"PII scan error: {e}",
            "auto_fix": "manual review required",
        }


def check_license_exists(repo_path: Path) -> dict:
    """Check if LICENSE file exists."""
    for name in ["LICENSE", "LICENSE.md", "LICENSE.txt"]:
        license_path = repo_path / name
        if license_path.exists():
            return {
                "check": "LICENSE_EXISTS",
                "passed": True,
                "path": str(license_path),
                "message": f"License found at {name}",
            }
    return {
        "check": "LICENSE_EXISTS",
        "passed": False,
        "path": None,
        "message": "No LICENSE file found",
        "auto_fix": "copy MIT license from template",
    }


def check_readme_has_license(repo_path: Path) -> dict:
    """Check if README references license."""
    readme_path = repo_path / "README.md"

    if not readme_path.exists():
        return {
            "check": "README_HAS_LICENSE",
            "passed": False,
            "message": "README.md does not exist",
            "auto_fix": "create README first",
        }

    try:
        content = readme_path.read_text(encoding="utf-8", errors="ignore")
        content_lower = content.lower()

        # Check for license section or MIT mention
        has_license = (
            "## license" in content_lower or
            "# license" in content_lower or
            "mit license" in content_lower or
            "[mit]" in content_lower
        )

        return {
            "check": "README_HAS_LICENSE",
            "passed": has_license,
            "message": "README references license" if has_license else "README missing license reference",
            "auto_fix": "append license section to README",
        }
    except Exception as e:
        return {
            "check": "README_HAS_LICENSE",
            "passed": False,
            "message": f"Error reading README: {e}",
            "auto_fix": "append license section to README",
        }


def check_claude_settings_sandbox(repo_path: Path) -> dict:
    """Check if repo has Claude settings with sandbox configuration."""
    claude_dir = repo_path / ".claude"
    settings_files = [
        claude_dir / "settings.json",
        claude_dir / "settings.local.json",
    ]

    # Also check CLAUDE.md for sandbox mention
    claude_md = repo_path / "CLAUDE.md"

    has_settings = any(f.exists() for f in settings_files)
    has_sandbox_mention = False

    if claude_md.exists():
        try:
            content = claude_md.read_text(encoding="utf-8", errors="ignore").lower()
            has_sandbox_mention = "sandbox" in content
        except Exception:
            pass

    # Check settings files for sandbox config
    for settings_file in settings_files:
        if settings_file.exists():
            try:
                content = settings_file.read_text(encoding="utf-8", errors="ignore").lower()
                if "sandbox" in content or "permissions" in content:
                    has_sandbox_mention = True
            except Exception:
                pass

    passed = has_settings or has_sandbox_mention

    return {
        "check": "CLAUDE_SETTINGS_SANDBOX",
        "passed": passed,
        "message": "Claude settings with sandbox config found" if passed else "Missing Claude sandbox settings",
        "has_settings_file": has_settings,
        "has_sandbox_mention": has_sandbox_mention,
        "auto_fix": "create .claude/settings.local.json and update CLAUDE.md",
    }


def check_python_pyproject(repo_path: Path) -> dict:
    """Check if Python project has pyproject.toml."""
    # Detect if it's a Python project
    python_indicators = [
        repo_path / "setup.py",
        repo_path / "requirements.txt",
        repo_path / "setup.cfg",
        repo_path / "Pipfile",
    ]

    is_python = any(f.exists() for f in python_indicators)

    # Also check for .py files
    if not is_python:
        py_files = list(repo_path.glob("*.py")) + list(repo_path.glob("**/*.py"))
        # Filter out test files and common non-package files
        is_python = len([f for f in py_files if not f.name.startswith("test_")]) > 2

    if not is_python:
        return {
            "check": "PYTHON_PYPROJECT",
            "passed": True,
            "message": "Not a Python project",
            "skipped": True,
        }

    pyproject_path = repo_path / "pyproject.toml"
    exists = pyproject_path.exists()

    return {
        "check": "PYTHON_PYPROJECT",
        "passed": exists,
        "path": str(pyproject_path) if exists else None,
        "message": "pyproject.toml exists" if exists else "Python project missing pyproject.toml",
        "auto_fix": "generate pyproject.toml",
    }


def check_python_uv_install(repo_path: Path) -> dict:
    """Check if Python project can be installed with uv."""
    pyproject_path = repo_path / "pyproject.toml"

    if not pyproject_path.exists():
        return {
            "check": "PYTHON_UV_INSTALL",
            "passed": False,
            "message": "No pyproject.toml to test",
            "skipped": True,
        }

    # Try uv sync --dry-run
    try:
        result = subprocess.run(
            ["uv", "sync", "--dry-run"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(repo_path),
        )

        if result.returncode == 0:
            return {
                "check": "PYTHON_UV_INSTALL",
                "passed": True,
                "message": "uv sync --dry-run succeeded",
            }
        else:
            return {
                "check": "PYTHON_UV_INSTALL",
                "passed": False,
                "message": f"uv sync failed: {result.stderr[:200]}",
                "auto_fix": "fix pyproject.toml",
            }

    except FileNotFoundError:
        return {
            "check": "PYTHON_UV_INSTALL",
            "passed": False,
            "message": "uv not installed",
            "skipped": True,
        }
    except subprocess.TimeoutExpired:
        return {
            "check": "PYTHON_UV_INSTALL",
            "passed": False,
            "message": "uv sync timed out",
            "auto_fix": "check pyproject.toml",
        }
    except Exception as e:
        return {
            "check": "PYTHON_UV_INSTALL",
            "passed": False,
            "message": f"Error: {e}",
            "skipped": True,
        }


def audit_repo(repo_path: Path) -> dict:
    """Run all checks on a single repository."""
    repo_path = Path(repo_path).resolve()

    checks = [
        check_readme_exists(repo_path),
        check_readme_current(repo_path),
        check_readme_has_license(repo_path),
        check_logo_exists(repo_path),
        check_license_exists(repo_path),
        check_gitignore_exists(repo_path),
        check_gitignore_complete(repo_path),
        check_claude_md_exists(repo_path),
        check_claude_settings_sandbox(repo_path),
        check_description_synced(repo_path),
        check_pii_clean(repo_path),
        check_python_pyproject(repo_path),
        check_python_uv_install(repo_path),
    ]

    passed = sum(1 for c in checks if c.get("passed") or c.get("skipped"))
    failed = sum(1 for c in checks if not c.get("passed") and not c.get("skipped"))

    return {
        "repo": repo_path.name,
        "path": str(repo_path),
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": passed,
            "failed": failed,
        },
    }


def run_audit(repos_dir: Path, repo_filter: str | None = None) -> dict:
    """
    Run audit on all repositories in directory.

    Args:
        repos_dir: Directory containing repositories
        repo_filter: Optional filter to match repo names

    Returns:
        Complete audit report as dict
    """
    repos_dir = Path(repos_dir).resolve()

    # Check dependencies first
    deps = check_dependencies()

    if not deps["git"]["available"]:
        return {
            "error": deps["git"]["error"],
            "dependency_check": deps,
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

    # Detect GitHub user
    github_user = detect_github_user(repos_dir)

    # Run audit on each repo
    results = []
    for repo in repos:
        results.append(audit_repo(repo))

    # Calculate overall summary
    total_checks = sum(r["summary"]["total"] for r in results)
    total_passed = sum(r["summary"]["passed"] for r in results)
    total_failed = sum(r["summary"]["failed"] for r in results)

    report = {
        "audit_time": datetime.now().isoformat(),
        "repos_dir": str(repos_dir),
        "github_user": github_user,
        "dependency_check": deps,
        "repos_count": len(repos),
        "repos": results,
        "summary": {
            "total_checks": total_checks,
            "passed": total_passed,
            "failed": total_failed,
            "pass_rate": round(total_passed / total_checks * 100, 1) if total_checks > 0 else 0,
        },
    }

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Audit repositories for standardization compliance"
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
        "--output",
        type=Path,
        help="Output file path (default: ~/.claude/repo-maintain-audit.json)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON to stdout",
    )

    args = parser.parse_args()

    # Run audit
    report = run_audit(args.repos_dir, args.filter)

    # Handle errors
    if "error" in report:
        print(f"Error: {report['error']}", file=sys.stderr)
        if args.json:
            print(json.dumps(report, indent=2))
        sys.exit(1)

    # Determine output path
    output_path = args.output
    if not output_path:
        claude_dir = Path.home() / ".claude"
        claude_dir.mkdir(exist_ok=True)
        output_path = claude_dir / "repo-maintain-audit.json"

    # Write report
    output_path.write_text(json.dumps(report, indent=2))

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Audit Report")
        print(f"============")
        print(f"Directory: {report['repos_dir']}")
        print(f"GitHub User: {report['github_user'] or 'Unknown'}")
        print(f"Repositories: {report['repos_count']}")
        print()
        print(f"Summary: {report['summary']['passed']}/{report['summary']['total_checks']} checks passed ({report['summary']['pass_rate']}%)")
        print()

        # Show failed checks by repo
        for repo_result in report["repos"]:
            failed_checks = [c for c in repo_result["checks"] if not c.get("passed") and not c.get("skipped")]
            if failed_checks:
                print(f"{repo_result['repo']}:")
                for check in failed_checks:
                    print(f"  - {check['check']}: {check['message']}")
                print()

        print(f"Report saved to: {output_path}")

    # Exit code based on results
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
