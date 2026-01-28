#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///
"""
Deterministically detect project type from file presence.

Usage:
    uv run shared/detect_project.py [--path <dir>] [--test]

Output:
    JSON: {"type": "python", "confidence": "high", "files": ["pyproject.toml"]}
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Detection rules: (file patterns, project type, confidence)
# Order matters - first match wins for primary type
DETECTION_RULES: List[Tuple[List[str], str, str]] = [
    # Node.js
    (["package.json"], "nodejs", "high"),
    # Python
    (["pyproject.toml"], "python", "high"),
    (["setup.py"], "python", "high"),
    (["requirements.txt"], "python", "medium"),
    (["Pipfile"], "python", "high"),
    # Rust
    (["Cargo.toml"], "rust", "high"),
    # Go
    (["go.mod"], "go", "high"),
    # Java/JVM
    (["pom.xml"], "java", "high"),
    (["build.gradle"], "java", "high"),
    (["build.gradle.kts"], "java", "high"),
    # .NET
    (["*.sln"], "dotnet", "high"),
    (["*.csproj"], "dotnet", "high"),
    (["*.fsproj"], "dotnet", "high"),
    # Ruby
    (["Gemfile"], "ruby", "high"),
    # PHP
    (["composer.json"], "php", "high"),
    # C/C++ (lower priority - Makefile is generic)
    (["CMakeLists.txt"], "cpp", "high"),
    (["Makefile"], "c", "low"),
]


def glob_match(pattern: str, files: List[str]) -> List[str]:
    """Simple glob matching for *.ext patterns."""
    if pattern.startswith("*."):
        ext = pattern[1:]  # includes the dot
        return [f for f in files if f.endswith(ext)]
    return [f for f in files if f == pattern]


def detect_project(path: Path) -> Dict:
    """Detect project type from files in the given directory."""
    if not path.is_dir():
        return {
            "type": "unknown",
            "confidence": "none",
            "files": [],
            "error": f"Path is not a directory: {path}"
        }

    # Get all files in root directory (not recursive for performance)
    try:
        root_files = [f.name for f in path.iterdir() if f.is_file()]
    except PermissionError:
        return {
            "type": "unknown",
            "confidence": "none",
            "files": [],
            "error": f"Permission denied: {path}"
        }

    detected_files = []
    detected_type = "unknown"
    confidence = "none"

    for patterns, proj_type, conf in DETECTION_RULES:
        for pattern in patterns:
            matches = glob_match(pattern, root_files)
            if matches:
                detected_files.extend(matches)
                if detected_type == "unknown":
                    detected_type = proj_type
                    confidence = conf
                break  # Only check first matching pattern per rule

    # Deduplicate while preserving order
    seen = set()
    unique_files = []
    for f in detected_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)

    return {
        "type": detected_type,
        "confidence": confidence,
        "files": unique_files
    }


def run_tests() -> bool:
    """Self-test with mock data."""
    import tempfile
    import shutil

    test_cases = [
        (["package.json"], "nodejs", "high"),
        (["pyproject.toml"], "python", "high"),
        (["requirements.txt"], "python", "medium"),
        (["Cargo.toml"], "rust", "high"),
        (["go.mod"], "go", "high"),
        (["pom.xml"], "java", "high"),
        (["Makefile"], "c", "low"),
        ([], "unknown", "none"),
    ]

    all_passed = True
    for files, expected_type, expected_conf in test_cases:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            for f in files:
                Path(tmpdir, f).touch()

            result = detect_project(Path(tmpdir))
            if result["type"] != expected_type:
                print(f"FAIL: {files} -> expected {expected_type}, got {result['type']}", file=sys.stderr)
                all_passed = False
            elif result["confidence"] != expected_conf:
                print(f"FAIL: {files} -> expected confidence {expected_conf}, got {result['confidence']}", file=sys.stderr)
                all_passed = False
            else:
                print(f"PASS: {files} -> {expected_type} ({expected_conf})")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Detect project type from file presence")
    parser.add_argument("--path", default=".", help="Directory to analyze (default: current)")
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    result = detect_project(Path(args.path).resolve())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
