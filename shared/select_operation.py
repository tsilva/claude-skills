#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///
"""
Determine skill operation from arguments and file state.

Usage:
    uv run shared/select_operation.py --skill <name> --args "<user args>" --check-files "file1,file2"

Output:
    JSON: {"operation": "modify", "reason": "README.md exists, no explicit operation"}
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Skill-specific operation rules
# Format: skill_name -> {
#   "operations": [list of valid operations],
#   "default_exists": operation when target file exists,
#   "default_missing": operation when target file is missing,
#   "keywords": {keyword: operation} for explicit matching
# }
SKILL_RULES: Dict[str, Dict] = {
    "readme": {
        "operations": ["create", "modify", "validate", "optimize"],
        "default_exists": "modify",
        "default_missing": "create",
        "keywords": {
            "create": "create",
            "new": "create",
            "generate": "create",
            "modify": "modify",
            "update": "modify",
            "edit": "modify",
            "change": "modify",
            "validate": "validate",
            "check": "validate",
            "verify": "validate",
            "score": "validate",
            "optimize": "optimize",
            "improve": "optimize",
            "fix": "optimize",
            "enhance": "optimize",
        },
        "primary_file": "README.md",
    },
    "project-readme-author": {
        "operations": ["create", "modify", "validate", "optimize"],
        "default_exists": "modify",
        "default_missing": "create",
        "keywords": {
            "create": "create",
            "new": "create",
            "generate": "create",
            "modify": "modify",
            "update": "modify",
            "edit": "modify",
            "change": "modify",
            "validate": "validate",
            "check": "validate",
            "verify": "validate",
            "score": "validate",
            "optimize": "optimize",
            "improve": "optimize",
            "fix": "optimize",
            "enhance": "optimize",
        },
        "primary_file": "README.md",
    },
    "repo-maintain": {
        "operations": ["audit", "fix"],
        "default_exists": "audit",
        "default_missing": "audit",
        "keywords": {
            "audit": "audit",
            "check": "audit",
            "scan": "audit",
            "analyze": "audit",
            "fix": "fix",
            "repair": "fix",
            "resolve": "fix",
            "apply": "fix",
        },
        "primary_file": None,  # No single primary file
    },
    "claude-skill-author": {
        "operations": ["create", "modify", "validate", "version"],
        "default_exists": "modify",
        "default_missing": "create",
        "keywords": {
            "create": "create",
            "new": "create",
            "generate": "create",
            "modify": "modify",
            "update": "modify",
            "edit": "modify",
            "validate": "validate",
            "check": "validate",
            "verify": "validate",
            "version": "version",
            "bump": "version",
            "release": "version",
        },
        "primary_file": "SKILL.md",
    },
    "project-logo-author": {
        "operations": ["create", "regenerate"],
        "default_exists": "regenerate",
        "default_missing": "create",
        "keywords": {
            "create": "create",
            "new": "create",
            "generate": "create",
            "regenerate": "regenerate",
            "redo": "regenerate",
            "replace": "regenerate",
        },
        "primary_file": "logo.png",
    },
}


def parse_keywords(args: str, keywords: Dict[str, str]) -> Optional[str]:
    """Extract operation from arguments by matching keywords."""
    if not args:
        return None

    args_lower = args.lower()

    # Check for exact operation name first
    for keyword, operation in keywords.items():
        # Match as whole word
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, args_lower):
            return operation

    return None


def check_files_exist(file_list: List[str], base_path: Path) -> Dict[str, bool]:
    """Check which files exist."""
    result = {}
    for file_name in file_list:
        file_path = base_path / file_name
        result[file_name] = file_path.exists()
    return result


def select_operation(
    skill: str,
    args: str,
    check_files: List[str],
    base_path: Path
) -> Dict:
    """Select the appropriate operation based on arguments and file state."""

    # Get skill rules
    rules = SKILL_RULES.get(skill)
    if not rules:
        return {
            "operation": None,
            "reason": f"Unknown skill: {skill}",
            "error": True,
            "valid_skills": list(SKILL_RULES.keys())
        }

    # Check for explicit operation in arguments
    explicit_op = parse_keywords(args, rules.get("keywords", {}))
    if explicit_op:
        return {
            "operation": explicit_op,
            "reason": f"Explicit keyword found in arguments",
            "source": "argument_keyword"
        }

    # Check file existence
    files_exist = check_files_exist(check_files, base_path)

    # Determine primary file status
    primary_file = rules.get("primary_file")
    if primary_file and primary_file in files_exist:
        primary_exists = files_exist[primary_file]
    elif check_files:
        # Use first file in list as primary if no explicit primary
        primary_exists = files_exist.get(check_files[0], False)
    else:
        primary_exists = False

    # Select based on file existence
    if primary_exists:
        operation = rules.get("default_exists", rules["operations"][0])
        reason = f"Primary file exists ({primary_file or check_files[0]})"
    else:
        operation = rules.get("default_missing", rules["operations"][0])
        reason = f"Primary file missing ({primary_file or check_files[0] if check_files else 'no files checked'})"

    return {
        "operation": operation,
        "reason": reason,
        "source": "file_state",
        "files_checked": files_exist
    }


def run_tests() -> bool:
    """Self-test the operation selection logic."""
    import tempfile

    all_passed = True

    # Test 1: Explicit keyword
    result = select_operation("readme", "please validate this", [], Path("."))
    if result["operation"] != "validate":
        print(f"FAIL: explicit keyword - expected validate, got {result['operation']}", file=sys.stderr)
        all_passed = False
    else:
        print("PASS: Explicit keyword detection")

    # Test 2: File exists -> modify
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "README.md").touch()
        result = select_operation("readme", "", ["README.md"], Path(tmpdir))
        if result["operation"] != "modify":
            print(f"FAIL: file exists - expected modify, got {result['operation']}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: File exists -> modify")

    # Test 3: File missing -> create
    with tempfile.TemporaryDirectory() as tmpdir:
        result = select_operation("readme", "", ["README.md"], Path(tmpdir))
        if result["operation"] != "create":
            print(f"FAIL: file missing - expected create, got {result['operation']}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: File missing -> create")

    # Test 4: Explicit keyword overrides file state
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "README.md").touch()
        result = select_operation("readme", "create a new readme", ["README.md"], Path(tmpdir))
        if result["operation"] != "create":
            print(f"FAIL: keyword override - expected create, got {result['operation']}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Keyword overrides file state")

    # Test 5: Unknown skill
    result = select_operation("unknown-skill", "", [], Path("."))
    if not result.get("error"):
        print(f"FAIL: unknown skill should return error", file=sys.stderr)
        all_passed = False
    else:
        print("PASS: Unknown skill handling")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Select skill operation from arguments and file state")
    parser.add_argument("--skill", required=False, help="Skill name (e.g., readme, repo-maintain)")
    parser.add_argument("--args", default="", help="User arguments to parse")
    parser.add_argument("--check-files", default="", help="Comma-separated list of files to check")
    parser.add_argument("--path", default=".", help="Base path for file checks (default: current)")
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    if not args.skill:
        parser.error("--skill is required")

    check_files = [f.strip() for f in args.check_files.split(",") if f.strip()]

    result = select_operation(
        skill=args.skill,
        args=args.args,
        check_files=check_files,
        base_path=Path(args.path).resolve()
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
