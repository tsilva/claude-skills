#!/usr/bin/env python3
"""
Repo Logo Generator - Generate contextual logos for GitHub repositories.

Analyzes project metadata (package.json, pyproject.toml, README.md, etc.) to
understand the project type and generate an appropriate visual logo.

Usage:
    python repo_logo_generator.py analyze [--readme PATH] [--cwd PATH]
    python repo_logo_generator.py generate --output PATH [OPTIONS]

Environment:
    SKILL_OPENROUTER_API_KEY - Required API key from https://openrouter.ai/keys

Examples:
    python repo_logo_generator.py analyze
    python repo_logo_generator.py generate --output /path/to/logo.png
    python repo_logo_generator.py generate --project-type cli --output /path/to/logo.png
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# Maps project types to visual metaphors and style guidance
PROJECT_METAPHORS = {
    "cli": {
        "metaphor": "origami paper transformation",
        "style": "geometric, clean lines, folded paper aesthetic",
        "description": "command transforms input like origami transforms paper"
    },
    "library": {
        "metaphor": "interconnected building blocks",
        "style": "modular, structured, interlocking pieces",
        "description": "reusable components that connect together"
    },
    "webapp": {
        "metaphor": "modern interface window with subtle depth",
        "style": "clean, minimal chrome, floating panels",
        "description": "digital window into functionality"
    },
    "api": {
        "metaphor": "messenger bird carrying a data packet",
        "style": "dynamic, flowing, in motion",
        "description": "swift communication between systems"
    },
    "framework": {
        "metaphor": "architectural scaffold or blueprint",
        "style": "solid, foundational, structural lines",
        "description": "foundation upon which applications are built"
    },
    "tool": {
        "metaphor": "precision instrument or Swiss army knife",
        "style": "functional, sharp edges, utilitarian beauty",
        "description": "focused instrument for specific tasks"
    },
    "converter": {
        "metaphor": "metamorphosis symbol, butterfly emerging",
        "style": "transformation, before/after, flowing transition",
        "description": "transforms one format into another"
    },
    "runner": {
        "metaphor": "sprinter in motion, speed lines",
        "style": "dynamic, energetic, forward momentum",
        "description": "executes tasks with speed and efficiency"
    },
    "validator": {
        "metaphor": "wax seal of approval",
        "style": "authoritative, trustworthy, official",
        "description": "confirms correctness and authenticity"
    },
    "linter": {
        "metaphor": "elegant brush sweeping away dust",
        "style": "refined, polishing motion, cleanliness",
        "description": "refines and cleans code"
    },
    "test": {
        "metaphor": "test tube with checkmarks or verification badges",
        "style": "scientific, precise, verification symbols",
        "description": "validates through systematic testing"
    },
    "dashboard": {
        "metaphor": "mission control panel with gauges",
        "style": "organized, overview perspective, data visualization",
        "description": "centralized view of system state"
    },
    "analytics": {
        "metaphor": "magnifying glass revealing hidden patterns",
        "style": "discovery, insight, revealing light",
        "description": "uncovers insights from data"
    },
    "default": {
        "metaphor": "abstract geometric shape suggesting innovation",
        "style": "clean, professional, modern",
        "description": "represents technical innovation"
    }
}

# Keywords that suggest project types
TYPE_KEYWORDS = {
    "cli": ["cli", "command", "terminal", "console", "shell", "cmd"],
    "library": ["lib", "library", "sdk", "package", "module"],
    "webapp": ["web", "app", "frontend", "ui", "dashboard", "portal"],
    "api": ["api", "rest", "graphql", "endpoint", "service", "server"],
    "framework": ["framework", "platform", "engine", "core"],
    "tool": ["tool", "utility", "util", "helper"],
    "converter": ["convert", "transform", "translate", "parse", "format"],
    "runner": ["runner", "executor", "run", "execute", "task"],
    "validator": ["validator", "validate", "check", "verify"],
    "linter": ["lint", "linter", "format", "prettier", "eslint"],
    "test": ["test", "spec", "jest", "pytest", "mocha"],
    "dashboard": ["dashboard", "monitor", "admin", "panel"],
    "analytics": ["analytics", "metrics", "stats", "tracking"]
}


class ProjectAnalyzer:
    """Analyzes project files to extract metadata."""

    def __init__(self, cwd: str = None):
        self.cwd = Path(cwd) if cwd else Path.cwd()

    def analyze(self, readme_path: str = None) -> dict:
        """Analyze project and return metadata."""
        result = {
            "name": None,
            "type": None,
            "description": None,
            "keywords": [],
            "suggested_metaphor": None
        }

        # Try to get info from various sources
        self._analyze_package_json(result)
        self._analyze_pyproject_toml(result)
        self._analyze_cargo_toml(result)

        # README can override or supplement
        if readme_path:
            self._analyze_readme(result, Path(readme_path))
        else:
            # Try to find README
            for name in ["README.md", "readme.md", "README.MD", "README"]:
                readme = self.cwd / name
                if readme.exists():
                    self._analyze_readme(result, readme)
                    break

        # Infer type from name/description if not found
        if not result["type"]:
            result["type"] = self._infer_type(result)

        # Set suggested metaphor
        type_key = result["type"] or "default"
        metaphor_info = PROJECT_METAPHORS.get(type_key, PROJECT_METAPHORS["default"])
        result["suggested_metaphor"] = metaphor_info["metaphor"]

        # Use directory name as fallback for project name
        if not result["name"]:
            result["name"] = self.cwd.name

        return result

    def _analyze_package_json(self, result: dict):
        """Extract info from package.json."""
        pkg_path = self.cwd / "package.json"
        if not pkg_path.exists():
            return

        try:
            with open(pkg_path) as f:
                pkg = json.load(f)

            if not result["name"]:
                result["name"] = pkg.get("name")
            if not result["description"]:
                result["description"] = pkg.get("description")

            result["keywords"].extend(pkg.get("keywords", []))

            # Check bin field for CLI
            if pkg.get("bin"):
                result["type"] = "cli"

        except (json.JSONDecodeError, IOError):
            pass

    def _analyze_pyproject_toml(self, result: dict):
        """Extract info from pyproject.toml."""
        toml_path = self.cwd / "pyproject.toml"
        if not toml_path.exists():
            return

        try:
            content = toml_path.read_text()

            # Simple TOML parsing for common fields
            name_match = re.search(r'^name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if name_match and not result["name"]:
                result["name"] = name_match.group(1)

            desc_match = re.search(r'^description\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if desc_match and not result["description"]:
                result["description"] = desc_match.group(1)

            # Check for CLI scripts
            if "[project.scripts]" in content or "[tool.poetry.scripts]" in content:
                result["type"] = "cli"

        except IOError:
            pass

    def _analyze_cargo_toml(self, result: dict):
        """Extract info from Cargo.toml."""
        cargo_path = self.cwd / "Cargo.toml"
        if not cargo_path.exists():
            return

        try:
            content = cargo_path.read_text()

            name_match = re.search(r'^name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if name_match and not result["name"]:
                result["name"] = name_match.group(1)

            desc_match = re.search(r'^description\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if desc_match and not result["description"]:
                result["description"] = desc_match.group(1)

            # Check for binary crate
            if "[[bin]]" in content:
                result["type"] = "cli"

        except IOError:
            pass

    def _analyze_readme(self, result: dict, readme_path: Path):
        """Extract info from README."""
        try:
            content = readme_path.read_text()

            # Get title from first heading
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match and not result["name"]:
                # Clean up the title (remove badges, links, etc.)
                title = title_match.group(1)
                title = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', title)  # Remove badge links
                title = re.sub(r'!\[.*?\]\(.*?\)', '', title)  # Remove images
                title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)  # Extract link text
                title = title.strip()
                if title:
                    result["name"] = title

            # Get description from first paragraph after title
            if not result["description"]:
                # Find first non-empty line after heading that isn't a badge
                lines = content.split('\n')
                in_header = True
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('#'):
                        in_header = False
                        continue
                    if in_header:
                        continue
                    # Skip badge lines
                    if line.startswith('[!') or line.startswith('<!'):
                        continue
                    # Skip HTML comments
                    if '<!--' in line:
                        continue
                    # Found description
                    result["description"] = line[:200]  # Limit length
                    break

        except IOError:
            pass

    def _infer_type(self, result: dict) -> str:
        """Infer project type from name, description, and keywords."""
        text = " ".join([
            result.get("name") or "",
            result.get("description") or "",
            " ".join(result.get("keywords", []))
        ]).lower()

        # Score each type by keyword matches
        scores = {}
        for proj_type, keywords in TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[proj_type] = score

        if scores:
            return max(scores, key=scores.get)

        return "default"


class OpenRouterImageClient:
    """Minimal OpenRouter client for image generation."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str):
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://claude.ai/claude-code",
            "X-Title": "Claude Code - Repo Logo Generator"
        }

    def generate_image(self, model: str, prompt: str, output_path: str) -> bool:
        """Generate an image and save it."""
        import base64
        import time

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": "1:1", "image_size": "1K"},
            "n": 1
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    images = result["choices"][0]["message"].get("images", [])

                    if images:
                        output = Path(output_path).resolve()
                        output.parent.mkdir(parents=True, exist_ok=True)

                        data_url = images[0]["image_url"]["url"]
                        base64_data = data_url.split(",")[1]

                        with open(output, "wb") as f:
                            f.write(base64.b64decode(base64_data))

                        print(f"Logo saved: {output}", file=sys.stderr)
                        return True
                    else:
                        print("No image generated by model", file=sys.stderr)
                        return False

                # Handle retryable errors
                if response.status_code in [408, 429, 502, 503] and attempt < max_retries - 1:
                    wait = min(2 ** attempt * 2, 30)
                    print(f"Retrying in {wait}s (attempt {attempt + 1}/{max_retries})...", file=sys.stderr)
                    time.sleep(wait)
                    continue

                # Non-retryable error
                error = response.json().get("error", {})
                message = error.get("message", response.text)
                print(f"OpenRouter error {response.status_code}: {message}", file=sys.stderr)
                return False

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    continue
                print("Request timed out", file=sys.stderr)
                return False
            except requests.exceptions.RequestException as e:
                print(f"Network error: {e}", file=sys.stderr)
                return False

        return False


def build_prompt(analysis: dict, style_override: str = None) -> str:
    """Build the image generation prompt from analysis."""
    name = analysis.get("name", "Project")
    proj_type = analysis.get("type", "default")
    description = analysis.get("description", "")

    metaphor_info = PROJECT_METAPHORS.get(proj_type, PROJECT_METAPHORS["default"])

    style = style_override or metaphor_info["style"]

    prompt = f"""Create a minimalist logo icon for a software project called "{name}".

Visual concept: {metaphor_info["metaphor"]} - {metaphor_info["description"]}.
{f'Project description: {description}' if description else ''}

Style requirements:
- {style}
- Clean vector style illustration
- NO TEXT or letters in the image
- Single centered focal point
- Works on both dark and light backgrounds
- Simple enough to be recognizable at 32x32 pixels
- Professional and modern aesthetic
- Flat design with subtle gradients if any

Generate a single, cohesive logo icon."""

    return prompt


def cmd_analyze(args):
    """Handle analyze command."""
    analyzer = ProjectAnalyzer(args.cwd)
    result = analyzer.analyze(args.readme)

    print(json.dumps(result, indent=2))


def cmd_generate(args):
    """Handle generate command."""
    # Get API key
    api_key = os.environ.get("SKILL_OPENROUTER_API_KEY")
    if not api_key:
        print("Error: SKILL_OPENROUTER_API_KEY environment variable not set", file=sys.stderr)
        print("Get your key at: https://openrouter.ai/keys", file=sys.stderr)
        sys.exit(1)

    # Analyze project (unless all overrides provided)
    if args.project_name and args.project_type:
        analysis = {
            "name": args.project_name,
            "type": args.project_type,
            "description": args.description or ""
        }
    else:
        analyzer = ProjectAnalyzer(args.cwd)
        analysis = analyzer.analyze(args.readme)

        # Apply overrides
        if args.project_name:
            analysis["name"] = args.project_name
        if args.project_type:
            analysis["type"] = args.project_type
        if args.description:
            analysis["description"] = args.description

    # Show what we're generating
    print(f"Generating logo for: {analysis['name']}", file=sys.stderr)
    print(f"Project type: {analysis['type']}", file=sys.stderr)

    # Build prompt and generate
    prompt = build_prompt(analysis, args.style)

    client = OpenRouterImageClient(api_key)
    success = client.generate_image(args.model, prompt, args.output)

    if not success:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate contextual logos for GitHub repositories"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze project and show detected metadata"
    )
    analyze_parser.add_argument(
        "--readme",
        help="Path to README.md (auto-detects if not specified)"
    )
    analyze_parser.add_argument(
        "--cwd",
        help="Working directory for project detection (defaults to current)"
    )

    # Generate command
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate a logo for the project"
    )
    gen_parser.add_argument(
        "--readme",
        help="Path to README.md for context extraction"
    )
    gen_parser.add_argument(
        "--cwd",
        help="Working directory for project detection"
    )
    gen_parser.add_argument(
        "--project-name",
        help="Override detected project name"
    )
    gen_parser.add_argument(
        "--project-type",
        choices=list(PROJECT_METAPHORS.keys()),
        help="Override detected project type"
    )
    gen_parser.add_argument(
        "--description",
        help="Override detected description"
    )
    gen_parser.add_argument(
        "--style",
        help="Style hint (minimalist, playful, corporate, tech)"
    )
    gen_parser.add_argument(
        "--model",
        default="google/gemini-2.0-flash-exp:free",
        help="OpenRouter model for image generation"
    )
    gen_parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output path for the logo PNG (required)"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "generate":
        cmd_generate(args)


if __name__ == "__main__":
    main()
