#!/usr/bin/env python3
"""
Internal validation hook for logo-generator.

Validates the bundled default-config.json against the expected schema.
This ensures config changes don't break existing user workflows.
"""

import argparse
import json
import sys
from pathlib import Path

# Schema definition: required keys for logo configuration
REQUIRED_LOGO_KEYS = {
    "model",
    "size",
    "promptTemplate",
    "style",
    "visualMetaphor",
    "includeRepoName",
    "iconColors",
    "additionalInstructions",
    "keyColor",
    "tolerance",
    "outputPath",
    "compress",
    "compressQuality",
}


def validate_default_config(skill_path: Path) -> list[dict]:
    """Validate bundled default-config.json against expected schema."""
    issues = []
    config_path = skill_path / "assets" / "default-config.json"

    if not config_path.exists():
        return [{
            "severity": "ERROR",
            "file_path": "assets/default-config.json",
            "field": "file",
            "message": "default-config.json not found"
        }]

    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError as e:
        return [{
            "severity": "ERROR",
            "file_path": "assets/default-config.json",
            "field": "json",
            "message": f"Invalid JSON: {e}"
        }]

    if "logo" not in config:
        return [{
            "severity": "ERROR",
            "file_path": "assets/default-config.json",
            "field": "logo",
            "message": "Missing required 'logo' key"
        }]

    logo = config["logo"]

    # Missing keys = ERROR
    missing_keys = REQUIRED_LOGO_KEYS - set(logo.keys())
    for key in sorted(missing_keys):
        issues.append({
            "severity": "ERROR",
            "file_path": "assets/default-config.json",
            "field": f"logo.{key}",
            "message": f"Missing required key '{key}'"
        })

    # Unknown keys = WARNING
    unknown_keys = set(logo.keys()) - REQUIRED_LOGO_KEYS
    for key in sorted(unknown_keys):
        issues.append({
            "severity": "WARNING",
            "file_path": "assets/default-config.json",
            "field": f"logo.{key}",
            "message": f"Unknown key '{key}' (not in schema)"
        })

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Internal validation hook for logo-generator"
    )
    parser.add_argument("skill_path", type=Path, help="Path to skill directory")
    parser.add_argument("--suggest", action="store_true", help="Include suggestions")
    args = parser.parse_args()

    issues = validate_default_config(args.skill_path)
    print(json.dumps({"issues": issues}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
