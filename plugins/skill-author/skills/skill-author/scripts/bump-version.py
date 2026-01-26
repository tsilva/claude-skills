#!/usr/bin/env python3
"""
Version bumping tool for skill plugins with semantic versioning support.

Claude-driven version management - Claude explicitly chooses the bump type
based on the changes made.

Usage:
  # Check if version already bumped in uncommitted changes
  python plugins/claude-skill-author/skills/claude-skill-author/scripts/bump-version.py <plugin-name> --check-uncommitted
  # Exit 0 = version already changed (skip bump)
  # Exit 1 = version not changed (needs bump)

  # Preview bump without applying
  python plugins/claude-skill-author/skills/claude-skill-author/scripts/bump-version.py <plugin-name> --type minor --dry-run

  # Apply bump
  python plugins/claude-skill-author/skills/claude-skill-author/scripts/bump-version.py <plugin-name> --type patch

Updates version in:
1. plugins/<plugin>/skills/<skill>/SKILL.md (metadata.version)
2. plugins/<plugin>/.claude-plugin/plugin.json (version)
3. .claude-plugin/marketplace.json (version for that plugin)
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def find_repo_root(start_path: Path) -> Path | None:
    """Find repository root by traversing upward to find .git or .claude-plugin/marketplace.json."""
    current = start_path.resolve()
    while current != current.parent:
        if (current / ".git").exists() or (current / ".claude-plugin" / "marketplace.json").exists():
            return current
        current = current.parent
    return None


def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse a version string into (major, minor, patch) tuple."""
    # Remove quotes if present
    version_str = version_str.strip().strip('"').strip("'")
    parts = version_str.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version_str}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def bump_version(version_str: str, bump_type: str) -> str:
    """Bump version based on type: major, minor, or patch."""
    major, minor, patch = parse_version(version_str)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def find_skill_md(plugin_dir: Path) -> Path | None:
    """Find the SKILL.md file for a plugin."""
    skills_dir = plugin_dir / "skills"
    if not skills_dir.exists():
        return None

    # Find the first skill directory with a SKILL.md
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                return skill_md
    return None


def extract_version_from_skill_md(skill_md_path: Path) -> str | None:
    """Extract version from SKILL.md frontmatter."""
    content = skill_md_path.read_text()

    # Match YAML frontmatter between --- markers
    match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    frontmatter = match.group(1)

    # Find version in metadata section
    # Look for: metadata:\n  ...\n  version: "X.Y.Z"
    version_match = re.search(r'^\s*version:\s*["\']?([^"\'\n]+)["\']?', frontmatter, re.MULTILINE)
    if version_match:
        return version_match.group(1).strip()

    return None


def check_uncommitted_version_change(skill_md_path: Path) -> bool:
    """Check if version line changed in uncommitted diff.

    Returns True if the version line has been modified (already bumped).
    Returns False if version line is unchanged (needs bumping).
    """
    result = subprocess.run(
        ["git", "diff", "--", str(skill_md_path)],
        capture_output=True, text=True
    )

    # Look for version line changes in diff (lines starting with + or -)
    for line in result.stdout.splitlines():
        if line.startswith(('+', '-')) and not line.startswith(('+++', '---')):
            if 'version:' in line.lower():
                return True
    return False


def update_skill_md(skill_md_path: Path, new_version: str, dry_run: bool = False) -> bool:
    """Update the version in SKILL.md frontmatter."""
    content = skill_md_path.read_text()

    # Match and replace version in frontmatter
    # Handle both quoted and unquoted versions
    new_content = re.sub(
        r'(^\s*version:\s*)["\']?[^"\'\n]+["\']?',
        f'\\1"{new_version}"',
        content,
        count=1,
        flags=re.MULTILINE
    )

    if new_content == content:
        return False

    if not dry_run:
        skill_md_path.write_text(new_content)
    return True


def update_plugin_json(plugin_json_path: Path, new_version: str, dry_run: bool = False) -> bool:
    """Update the version in plugin.json."""
    if not plugin_json_path.exists():
        return False

    with open(plugin_json_path) as f:
        data = json.load(f)

    old_version = data.get("version")
    if old_version == new_version:
        return False

    data["version"] = new_version

    if not dry_run:
        with open(plugin_json_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")  # Add trailing newline

    return True


def update_marketplace_json(marketplace_path: Path, plugin_name: str, new_version: str, dry_run: bool = False) -> bool:
    """Update the version for a plugin in marketplace.json."""
    if not marketplace_path.exists():
        return False

    with open(marketplace_path) as f:
        data = json.load(f)

    plugins = data.get("plugins", [])
    updated = False

    for plugin in plugins:
        if plugin.get("name") == plugin_name:
            if plugin.get("version") != new_version:
                plugin["version"] = new_version
                updated = True
            break

    if updated and not dry_run:
        with open(marketplace_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")  # Add trailing newline

    return updated


def main():
    parser = argparse.ArgumentParser(
        description="Bump version numbers for a skill plugin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check if version already bumped in uncommitted changes
  python plugins/claude-skill-author/skills/claude-skill-author/scripts/bump-version.py readme-generator --check-uncommitted

  # Preview what would be bumped
  python plugins/claude-skill-author/skills/claude-skill-author/scripts/bump-version.py readme-generator --type minor --dry-run

  # Apply version bump
  python plugins/claude-skill-author/skills/claude-skill-author/scripts/bump-version.py readme-generator --type patch
"""
    )
    parser.add_argument("plugin_name", help="Name of the plugin to bump version for")
    parser.add_argument(
        "--type", "-t",
        choices=["patch", "minor", "major"],
        help="Type of version bump (required when bumping)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be bumped without making changes"
    )
    parser.add_argument(
        "--check-uncommitted",
        action="store_true",
        help="Check if version line already changed in uncommitted diff. Exit 0 if changed, 1 if not."
    )

    args = parser.parse_args()

    # Find repo root by traversing upward
    script_dir = Path(__file__).resolve().parent
    repo_root = find_repo_root(script_dir)
    if not repo_root:
        print("Error: Could not find repository root (no .git or .claude-plugin/marketplace.json found)", file=sys.stderr)
        sys.exit(1)

    # Locate plugin directory
    plugin_dir = repo_root / "plugins" / args.plugin_name
    if not plugin_dir.exists():
        print(f"Error: Plugin directory not found: {plugin_dir}", file=sys.stderr)
        sys.exit(1)

    # Find SKILL.md
    skill_md_path = find_skill_md(plugin_dir)
    if not skill_md_path:
        print(f"Error: SKILL.md not found for plugin: {args.plugin_name}", file=sys.stderr)
        sys.exit(1)

    # Handle --check-uncommitted mode
    if args.check_uncommitted:
        if check_uncommitted_version_change(skill_md_path):
            print(f"Version already changed in uncommitted diff: {skill_md_path.relative_to(repo_root)}")
            sys.exit(0)  # Already bumped
        else:
            print(f"Version not changed in uncommitted diff: {skill_md_path.relative_to(repo_root)}")
            sys.exit(1)  # Needs bump

    # For actual bumping, --type is required
    if not args.type:
        print("Error: --type is required when bumping version (choose: patch, minor, major)", file=sys.stderr)
        sys.exit(1)

    plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"

    # Extract current version
    current_version = extract_version_from_skill_md(skill_md_path)
    if not current_version:
        print(f"Error: Could not extract version from {skill_md_path}", file=sys.stderr)
        sys.exit(1)

    # Bump version
    new_version = bump_version(current_version, args.type)

    mode_str = "[DRY RUN] " if args.dry_run else ""
    print(f"{mode_str}Bumping version ({args.type}): {current_version} -> {new_version}")

    # Update all files
    updates = []

    if update_skill_md(skill_md_path, new_version, args.dry_run):
        updates.append(f"  {'Would update' if args.dry_run else 'Updated'}: {skill_md_path.relative_to(repo_root)}")

    if update_plugin_json(plugin_json_path, new_version, args.dry_run):
        updates.append(f"  {'Would update' if args.dry_run else 'Updated'}: {plugin_json_path.relative_to(repo_root)}")

    if update_marketplace_json(marketplace_path, args.plugin_name, new_version, args.dry_run):
        updates.append(f"  {'Would update' if args.dry_run else 'Updated'}: {marketplace_path.relative_to(repo_root)}")

    for update in updates:
        print(update)

    if not updates:
        print("  No files needed updating.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
