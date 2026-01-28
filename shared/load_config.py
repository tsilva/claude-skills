#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///
"""
Load and merge multi-level JSON configs with proper precedence.

Usage:
    uv run shared/load_config.py --defaults <file> [--user <file>] [--project <file>]

Precedence: project > user > defaults

Output:
    Merged JSON config to stdout
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def expand_env_vars(value: Any) -> Any:
    """Recursively expand environment variables in strings."""
    if isinstance(value, str):
        # Handle $VAR and ${VAR} patterns
        def replace_var(match):
            var_name = match.group(1) or match.group(2)
            return os.environ.get(var_name, match.group(0))

        # Match $VAR or ${VAR}
        pattern = r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
        return re.sub(pattern, replace_var, value)
    elif isinstance(value, dict):
        return {k: expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [expand_env_vars(item) for item in value]
    return value


def deep_merge(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries. Override takes precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_json_file(path: Path) -> Optional[Dict]:
    """Load JSON file, returning None if not found or invalid."""
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in {path}: {e}", file=sys.stderr)
        return None
    except PermissionError:
        print(f"Warning: Permission denied reading {path}", file=sys.stderr)
        return None


def load_config(
    defaults_path: Optional[str] = None,
    user_path: Optional[str] = None,
    project_path: Optional[str] = None,
    expand_env: bool = True
) -> Dict:
    """Load and merge configs with precedence: project > user > defaults."""
    result: Dict[str, Any] = {}

    # Load in order of precedence (lowest to highest)
    paths = [
        (defaults_path, "defaults"),
        (user_path, "user"),
        (project_path, "project"),
    ]

    loaded_sources = []

    for path_str, source_name in paths:
        if path_str:
            # Expand ~ for home directory
            expanded_path = os.path.expanduser(path_str)
            path = Path(expanded_path)
            config = load_json_file(path)
            if config is not None:
                result = deep_merge(result, config)
                loaded_sources.append(source_name)

    # Expand environment variables if requested
    if expand_env:
        result = expand_env_vars(result)

    # Add metadata about what was loaded
    result["_meta"] = {
        "sources": loaded_sources
    }

    return result


def run_tests() -> bool:
    """Self-test with temporary files."""
    import tempfile

    all_passed = True

    # Test 1: Basic merge
    with tempfile.TemporaryDirectory() as tmpdir:
        defaults = Path(tmpdir, "defaults.json")
        user = Path(tmpdir, "user.json")
        project = Path(tmpdir, "project.json")

        defaults.write_text('{"a": 1, "b": {"x": 10}}')
        user.write_text('{"b": {"y": 20}}')
        project.write_text('{"a": 100}')

        result = load_config(str(defaults), str(user), str(project))

        if result.get("a") != 100:
            print(f"FAIL: project override - expected a=100, got {result.get('a')}", file=sys.stderr)
            all_passed = False
        elif result.get("b", {}).get("x") != 10:
            print(f"FAIL: deep merge - expected b.x=10", file=sys.stderr)
            all_passed = False
        elif result.get("b", {}).get("y") != 20:
            print(f"FAIL: deep merge - expected b.y=20", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Basic merge")

    # Test 2: Missing files handled gracefully
    with tempfile.TemporaryDirectory() as tmpdir:
        defaults = Path(tmpdir, "defaults.json")
        defaults.write_text('{"key": "value"}')

        result = load_config(str(defaults), "/nonexistent/user.json", "/nonexistent/project.json")

        if result.get("key") != "value":
            print(f"FAIL: missing files - expected key=value", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Missing files handled")

    # Test 3: Environment variable expansion
    os.environ["TEST_VAR"] = "expanded_value"
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Path(tmpdir, "config.json")
        config.write_text('{"path": "$TEST_VAR", "path2": "${TEST_VAR}"}')

        result = load_config(str(config))

        if result.get("path") != "expanded_value":
            print(f"FAIL: env expansion $VAR - expected expanded_value, got {result.get('path')}", file=sys.stderr)
            all_passed = False
        elif result.get("path2") != "expanded_value":
            print(f"FAIL: env expansion ${{VAR}} - expected expanded_value, got {result.get('path2')}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Environment variable expansion")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Load and merge JSON configs")
    parser.add_argument("--defaults", help="Path to defaults config file")
    parser.add_argument("--user", help="Path to user config file")
    parser.add_argument("--project", help="Path to project config file")
    parser.add_argument("--no-expand-env", action="store_true", help="Disable environment variable expansion")
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    if not any([args.defaults, args.user, args.project]):
        parser.error("At least one config file path must be provided")

    result = load_config(
        defaults_path=args.defaults,
        user_path=args.user,
        project_path=args.project,
        expand_env=not args.no_expand_env
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
