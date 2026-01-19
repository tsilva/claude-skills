#!/usr/bin/env python3
"""
Validate skills against the Agent Skills specification (agentskills.io/specification)
and repository-specific rules from CLAUDE.md.

Usage:
    python scripts/validate_skills.py              # Validate all skills
    python scripts/validate_skills.py --verbose    # Show all details
    python scripts/validate_skills.py --plugin foo # Validate single plugin

Exit codes: 0 = passed, 1 = failed
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(Enum):
    """Validation issue severity level."""
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass
class ValidationIssue:
    """A single validation issue."""
    severity: Severity
    file_path: str
    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.severity.value}: {self.file_path} [{self.field}]: {self.message}"


@dataclass
class SkillValidationResult:
    """Validation result for a single skill."""
    plugin_name: str
    skill_name: str
    skill_md_path: Path
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == Severity.WARNING for i in self.issues)


@dataclass
class ValidationReport:
    """Complete validation report."""
    skill_results: list[SkillValidationResult] = field(default_factory=list)
    global_issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def total_errors(self) -> int:
        count = sum(1 for i in self.global_issues if i.severity == Severity.ERROR)
        for result in self.skill_results:
            count += sum(1 for i in result.issues if i.severity == Severity.ERROR)
        return count

    @property
    def total_warnings(self) -> int:
        count = sum(1 for i in self.global_issues if i.severity == Severity.WARNING)
        for result in self.skill_results:
            count += sum(1 for i in result.issues if i.severity == Severity.WARNING)
        return count

    @property
    def passed(self) -> bool:
        return self.total_errors == 0


# =============================================================================
# YAML Frontmatter Parser (regex-based, no PyYAML dependency)
# =============================================================================

def parse_skill_md(skill_md_path: Path) -> tuple[dict[str, Any], str, int]:
    """
    Parse a SKILL.md file and extract frontmatter and body.

    Returns:
        (frontmatter_dict, body_text, body_line_count)
    """
    content = skill_md_path.read_text()

    # Match YAML frontmatter between --- markers
    match = re.search(r"^---\s*\n(.*?)\n---\s*\n?", content, re.DOTALL)
    if not match:
        return {}, content, content.count('\n') + 1

    frontmatter_text = match.group(1)
    body = content[match.end():]
    body_line_count = body.count('\n') + 1 if body.strip() else 0

    # Parse simple YAML (handles top-level and one-level nested keys)
    frontmatter = parse_simple_yaml(frontmatter_text)

    return frontmatter, body, body_line_count


def parse_simple_yaml(text: str) -> dict[str, Any]:
    """
    Parse simple YAML frontmatter without PyYAML.
    Handles:
    - Top-level scalar values: key: value
    - Nested objects: key:\n  subkey: value
    - Quoted strings
    """
    result: dict[str, Any] = {}
    lines = text.split('\n')
    current_key = None
    current_indent = 0
    nested_content: list[str] = []

    for line in lines:
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            continue

        # Calculate indentation
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # Check if this is a new top-level key
        if indent == 0 and ':' in stripped:
            # Process any pending nested content
            if current_key and nested_content:
                result[current_key] = parse_nested_yaml(nested_content)
                nested_content = []

            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip()

            if value:
                # Simple key: value pair
                result[key] = parse_yaml_value(value)
                current_key = None
            else:
                # Key with nested content
                current_key = key
                current_indent = 0
        elif current_key and indent > 0:
            # Nested content
            nested_content.append(line)

    # Process any remaining nested content
    if current_key and nested_content:
        result[current_key] = parse_nested_yaml(nested_content)

    return result


def parse_nested_yaml(lines: list[str]) -> dict[str, Any]:
    """Parse nested YAML content (one level deep)."""
    result: dict[str, Any] = {}
    for line in lines:
        stripped = line.strip()
        if ':' in stripped and not stripped.startswith('#'):
            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip()
            if value:
                result[key] = parse_yaml_value(value)
    return result


def parse_yaml_value(value: str) -> str:
    """Parse a YAML value, handling quotes."""
    value = value.strip()
    # Remove surrounding quotes
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


# =============================================================================
# Validators
# =============================================================================

def validate_name(
    name: str | None,
    skill_dir_name: str,
    file_path: str
) -> list[ValidationIssue]:
    """
    Validate the 'name' field against Agent Skills spec and repo rules.

    Rules:
    - Required, 1-64 characters
    - Lowercase letters, numbers, hyphens only
    - No leading/trailing hyphens
    - No consecutive hyphens (--)
    - Must match parent directory name
    - Cannot contain "anthropic" or "claude" (repo rule)
    """
    issues = []

    if not name:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            "'name' is required but missing"
        ))
        return issues

    # Length check
    if len(name) > 64:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            f"'name' exceeds 64 characters ({len(name)} chars)"
        ))

    if len(name) < 1:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            "'name' must be at least 1 character"
        ))

    # Character validation: lowercase, numbers, hyphens only
    if not re.match(r'^[a-z0-9-]+$', name):
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            f"'name' must contain only lowercase letters, numbers, and hyphens (got: '{name}')"
        ))

    # No leading/trailing hyphens
    if name.startswith('-') or name.endswith('-'):
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            f"'name' cannot start or end with a hyphen (got: '{name}')"
        ))

    # No consecutive hyphens
    if '--' in name:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            f"'name' cannot contain consecutive hyphens (got: '{name}')"
        ))

    # Must match directory name
    if name != skill_dir_name:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            f"'name' must match parent directory (name='{name}', dir='{skill_dir_name}')"
        ))

    # Repo-specific: no "anthropic" or "claude"
    name_lower = name.lower()
    if 'anthropic' in name_lower:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            "'name' cannot contain 'anthropic'"
        ))
    if 'claude' in name_lower:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            "'name' cannot contain 'claude'"
        ))

    return issues


def validate_description(description: str | None, file_path: str) -> list[ValidationIssue]:
    """
    Validate the 'description' field.

    Rules:
    - Required, 1-1024 characters
    - Non-empty (not just whitespace)
    """
    issues = []

    if description is None:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "description",
            "'description' is required but missing"
        ))
        return issues

    if not description.strip():
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "description",
            "'description' cannot be empty or whitespace-only"
        ))
        return issues

    if len(description) > 1024:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "description",
            f"'description' exceeds 1024 characters ({len(description)} chars)"
        ))

    return issues


def validate_optional_fields(frontmatter: dict[str, Any], file_path: str) -> list[ValidationIssue]:
    """
    Validate optional frontmatter fields.

    Fields:
    - license: string (no constraints)
    - compatibility: max 500 chars
    - metadata: key-value mapping
    - allowed-tools: space-delimited string
    """
    issues = []

    # Compatibility length check
    compatibility = frontmatter.get('compatibility')
    if compatibility and len(str(compatibility)) > 500:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "compatibility",
            f"'compatibility' exceeds 500 characters ({len(str(compatibility))} chars)"
        ))

    # Metadata type check
    metadata = frontmatter.get('metadata')
    if metadata is not None and not isinstance(metadata, dict):
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "metadata",
            f"'metadata' must be a key-value mapping, got {type(metadata).__name__}"
        ))

    # allowed-tools type check
    allowed_tools = frontmatter.get('allowed-tools')
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "allowed-tools",
            f"'allowed-tools' must be a space-delimited string, got {type(allowed_tools).__name__}"
        ))

    return issues


def validate_body(body_line_count: int, file_path: str) -> list[ValidationIssue]:
    """
    Validate SKILL.md body.

    Rules:
    - Warning if body exceeds 500 lines (repo guideline)
    """
    issues = []

    if body_line_count > 500:
        issues.append(ValidationIssue(
            Severity.WARNING, file_path, "body",
            f"Body exceeds 500 lines ({body_line_count} lines) - consider reducing for token efficiency"
        ))

    return issues


def validate_plugin_json(plugin_json_path: Path, repo_root: Path) -> list[ValidationIssue]:
    """
    Validate plugin.json schema.

    Required fields: name, description, version, author.name
    """
    issues = []
    rel_path = str(plugin_json_path.relative_to(repo_root))

    if not plugin_json_path.exists():
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "file",
            "plugin.json file is missing"
        ))
        return issues

    try:
        with open(plugin_json_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "json",
            f"Invalid JSON: {e}"
        ))
        return issues

    # Required fields
    required = ['name', 'description', 'version']
    for field_name in required:
        if field_name not in data:
            issues.append(ValidationIssue(
                Severity.ERROR, rel_path, field_name,
                f"Required field '{field_name}' is missing"
            ))
        elif not data[field_name]:
            issues.append(ValidationIssue(
                Severity.ERROR, rel_path, field_name,
                f"Required field '{field_name}' is empty"
            ))

    # author.name required
    author = data.get('author', {})
    if not isinstance(author, dict):
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "author",
            "'author' must be an object"
        ))
    elif 'name' not in author or not author['name']:
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "author.name",
            "Required field 'author.name' is missing or empty"
        ))

    return issues


def validate_version_sync(
    skill_md_path: Path,
    plugin_json_path: Path,
    marketplace_path: Path,
    plugin_name: str,
    repo_root: Path
) -> list[ValidationIssue]:
    """
    Validate that versions are synchronized across all files.

    Checks: SKILL.md metadata.version, plugin.json version, marketplace.json version
    """
    issues = []
    versions: dict[str, str | None] = {}

    # Get version from SKILL.md metadata
    if skill_md_path.exists():
        frontmatter, _, _ = parse_skill_md(skill_md_path)
        metadata = frontmatter.get('metadata', {})
        if isinstance(metadata, dict):
            versions['SKILL.md'] = metadata.get('version')

    # Get version from plugin.json
    if plugin_json_path.exists():
        try:
            with open(plugin_json_path) as f:
                data = json.load(f)
                versions['plugin.json'] = data.get('version')
        except (json.JSONDecodeError, IOError):
            pass

    # Get version from marketplace.json
    if marketplace_path.exists():
        try:
            with open(marketplace_path) as f:
                data = json.load(f)
                for plugin in data.get('plugins', []):
                    if plugin.get('name') == plugin_name:
                        versions['marketplace.json'] = plugin.get('version')
                        break
        except (json.JSONDecodeError, IOError):
            pass

    # Check if all present versions match
    present_versions = {k: v for k, v in versions.items() if v is not None}

    if len(present_versions) > 1:
        unique_versions = set(present_versions.values())
        if len(unique_versions) > 1:
            version_details = ', '.join(f"{k}={v}" for k, v in present_versions.items())
            rel_path = str(skill_md_path.relative_to(repo_root))
            issues.append(ValidationIssue(
                Severity.ERROR, rel_path, "version",
                f"Version mismatch across files: {version_details}"
            ))

    return issues


def validate_marketplace_json(marketplace_path: Path, repo_root: Path) -> list[ValidationIssue]:
    """
    Validate marketplace.json global schema.

    Required: name, description, owner.name, plugins[] with name, source, description, version
    """
    issues = []
    rel_path = str(marketplace_path.relative_to(repo_root))

    if not marketplace_path.exists():
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "file",
            "marketplace.json file is missing"
        ))
        return issues

    try:
        with open(marketplace_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "json",
            f"Invalid JSON: {e}"
        ))
        return issues

    # Top-level required fields
    for field_name in ['name', 'description']:
        if field_name not in data:
            issues.append(ValidationIssue(
                Severity.ERROR, rel_path, field_name,
                f"Required field '{field_name}' is missing"
            ))

    # owner.name required
    owner = data.get('owner', {})
    if not isinstance(owner, dict):
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "owner",
            "'owner' must be an object"
        ))
    elif 'name' not in owner or not owner['name']:
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "owner.name",
            "Required field 'owner.name' is missing or empty"
        ))

    # Validate plugins array
    plugins = data.get('plugins', [])
    if not isinstance(plugins, list):
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "plugins",
            "'plugins' must be an array"
        ))
        return issues

    for i, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            issues.append(ValidationIssue(
                Severity.ERROR, rel_path, f"plugins[{i}]",
                "Each plugin must be an object"
            ))
            continue

        plugin_name = plugin.get('name', f'plugins[{i}]')
        for field_name in ['name', 'source', 'description', 'version']:
            if field_name not in plugin:
                issues.append(ValidationIssue(
                    Severity.ERROR, rel_path, f"plugins.{plugin_name}.{field_name}",
                    f"Required field '{field_name}' is missing in plugin '{plugin_name}'"
                ))
            elif not plugin[field_name]:
                issues.append(ValidationIssue(
                    Severity.ERROR, rel_path, f"plugins.{plugin_name}.{field_name}",
                    f"Required field '{field_name}' is empty in plugin '{plugin_name}'"
                ))

    return issues


# =============================================================================
# Skill Discovery
# =============================================================================

def discover_skills(plugins_dir: Path) -> list[tuple[str, str, Path]]:
    """
    Discover all skills in the plugins directory.

    Returns:
        List of (plugin_name, skill_name, skill_md_path) tuples
    """
    skills = []

    if not plugins_dir.exists():
        return skills

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        skills_dir = plugin_dir / "skills"
        if not skills_dir.exists():
            continue

        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                skills.append((plugin_dir.name, skill_dir.name, skill_md))

    return skills


# =============================================================================
# Main Validation Logic
# =============================================================================

def validate_skill(
    plugin_name: str,
    skill_name: str,
    skill_md_path: Path,
    repo_root: Path
) -> SkillValidationResult:
    """Validate a single skill."""
    result = SkillValidationResult(
        plugin_name=plugin_name,
        skill_name=skill_name,
        skill_md_path=skill_md_path
    )

    rel_path = str(skill_md_path.relative_to(repo_root))

    # Parse SKILL.md
    try:
        frontmatter, body, body_line_count = parse_skill_md(skill_md_path)
    except Exception as e:
        result.issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "parse",
            f"Failed to parse SKILL.md: {e}"
        ))
        return result

    # Get skill directory name for validation
    skill_dir_name = skill_md_path.parent.name

    # Validate frontmatter fields
    result.issues.extend(validate_name(
        frontmatter.get('name'),
        skill_dir_name,
        rel_path
    ))

    result.issues.extend(validate_description(
        frontmatter.get('description'),
        rel_path
    ))

    result.issues.extend(validate_optional_fields(frontmatter, rel_path))

    # Validate body
    result.issues.extend(validate_body(body_line_count, rel_path))

    # Validate plugin.json
    plugin_json_path = repo_root / "plugins" / plugin_name / ".claude-plugin" / "plugin.json"
    result.issues.extend(validate_plugin_json(plugin_json_path, repo_root))

    # Validate version sync
    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"
    result.issues.extend(validate_version_sync(
        skill_md_path,
        plugin_json_path,
        marketplace_path,
        plugin_name,
        repo_root
    ))

    return result


def run_validation(repo_root: Path, plugin_filter: str | None = None) -> ValidationReport:
    """Run full validation and return report."""
    report = ValidationReport()

    plugins_dir = repo_root / "plugins"
    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"

    # Validate marketplace.json (global)
    report.global_issues.extend(validate_marketplace_json(marketplace_path, repo_root))

    # Discover and validate skills
    skills = discover_skills(plugins_dir)

    for plugin_name, skill_name, skill_md_path in skills:
        if plugin_filter and plugin_name != plugin_filter:
            continue

        result = validate_skill(plugin_name, skill_name, skill_md_path, repo_root)
        report.skill_results.append(result)

    return report


def print_report(report: ValidationReport, verbose: bool = False) -> None:
    """Print validation report to stdout."""
    all_issues: list[ValidationIssue] = list(report.global_issues)
    for result in report.skill_results:
        all_issues.extend(result.issues)

    # Print issues
    for issue in all_issues:
        print(issue)

    if all_issues:
        print()

    # Print summary
    skill_count = len(report.skill_results)
    print(f"Validated {skill_count} skill(s)")
    print(f"  Errors: {report.total_errors}")
    print(f"  Warnings: {report.total_warnings}")

    if verbose:
        print("\nSkills validated:")
        for result in report.skill_results:
            status = "FAIL" if result.has_errors else ("WARN" if result.has_warnings else "OK")
            print(f"  [{status}] {result.plugin_name}/{result.skill_name}")

    print()
    if report.passed:
        print("Validation PASSED")
    else:
        print("Validation FAILED")


# =============================================================================
# CLI
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate skills against Agent Skills specification"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output including all validated skills"
    )
    parser.add_argument(
        "--plugin", "-p",
        type=str,
        help="Validate only the specified plugin"
    )

    args = parser.parse_args()

    # Determine repo root (script is in scripts/)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    # Run validation
    report = run_validation(repo_root, plugin_filter=args.plugin)

    # Print report
    print_report(report, verbose=args.verbose)

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
