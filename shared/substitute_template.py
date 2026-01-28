#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///
"""
Replace {VARIABLE} placeholders in templates with values.

Usage:
    uv run shared/substitute_template.py --template "path/to/template.txt" --vars '{"KEY": "value"}'

Output:
    Substituted template content to stdout
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def find_placeholders(content: str) -> Set[str]:
    """Find all {VARIABLE} placeholders in content."""
    pattern = r'\{([A-Z][A-Z0-9_]*)\}'
    return set(re.findall(pattern, content))


def substitute(content: str, variables: Dict[str, str]) -> Tuple[str, List[str]]:
    """
    Replace {VARIABLE} placeholders with values.

    Returns:
        Tuple of (substituted content, list of unsubstituted variables)
    """
    placeholders = find_placeholders(content)
    unsubstituted = []

    result = content
    for placeholder in placeholders:
        if placeholder in variables:
            # Replace all occurrences of {PLACEHOLDER}
            result = result.replace(f"{{{placeholder}}}", str(variables[placeholder]))
        else:
            unsubstituted.append(placeholder)

    return result, sorted(unsubstituted)


def run_tests() -> bool:
    """Self-test the substitution logic."""
    all_passed = True

    # Test 1: Basic substitution
    content = "Hello {NAME}, welcome to {PROJECT}!"
    variables = {"NAME": "Alice", "PROJECT": "TestApp"}
    result, missing = substitute(content, variables)

    if result != "Hello Alice, welcome to TestApp!":
        print(f"FAIL: basic substitution - got: {result}", file=sys.stderr)
        all_passed = False
    elif missing:
        print(f"FAIL: basic substitution - unexpected missing: {missing}", file=sys.stderr)
        all_passed = False
    else:
        print("PASS: Basic substitution")

    # Test 2: Missing variables
    content = "Hello {NAME}, your {ROLE} is ready"
    variables = {"NAME": "Bob"}
    result, missing = substitute(content, variables)

    if "ROLE" not in missing:
        print(f"FAIL: missing detection - ROLE not in missing: {missing}", file=sys.stderr)
        all_passed = False
    elif "{ROLE}" not in result:
        print(f"FAIL: missing preserved - {ROLE} should remain in output", file=sys.stderr)
        all_passed = False
    else:
        print("PASS: Missing variable detection")

    # Test 3: No placeholders
    content = "Plain text without placeholders"
    result, missing = substitute(content, {"UNUSED": "value"})

    if result != content:
        print(f"FAIL: no placeholders - content changed unexpectedly", file=sys.stderr)
        all_passed = False
    elif missing:
        print(f"FAIL: no placeholders - unexpected missing: {missing}", file=sys.stderr)
        all_passed = False
    else:
        print("PASS: No placeholders")

    # Test 4: Multiple occurrences
    content = "{NAME} said hello. {NAME} left."
    variables = {"NAME": "Charlie"}
    result, missing = substitute(content, variables)

    if result != "Charlie said hello. Charlie left.":
        print(f"FAIL: multiple occurrences - got: {result}", file=sys.stderr)
        all_passed = False
    else:
        print("PASS: Multiple occurrences")

    # Test 5: Case sensitivity (lowercase should not match)
    content = "Hello {name} and {NAME}"
    variables = {"NAME": "Dave"}
    result, missing = substitute(content, variables)

    if "{name}" not in result:
        print(f"FAIL: case sensitivity - lowercase should not match", file=sys.stderr)
        all_passed = False
    elif "Dave" not in result:
        print(f"FAIL: case sensitivity - NAME should be replaced", file=sys.stderr)
        all_passed = False
    else:
        print("PASS: Case sensitivity")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Substitute template variables")
    parser.add_argument("--template", help="Path to template file")
    parser.add_argument("--vars", default="{}", help="JSON object of variables")
    parser.add_argument("--warn-missing", action="store_true", help="Warn about unsubstituted variables")
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    if not args.template:
        parser.error("--template is required")

    # Load template
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"Error: Template file not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    try:
        content = template_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading template: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse variables
    try:
        variables = json.loads(args.vars)
    except json.JSONDecodeError as e:
        print(f"Error parsing --vars JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Perform substitution
    result, missing = substitute(content, variables)

    # Warn about missing variables
    if args.warn_missing and missing:
        print(f"Warning: Unsubstituted variables: {', '.join(missing)}", file=sys.stderr)

    # Output result
    print(result, end='')


if __name__ == "__main__":
    main()
