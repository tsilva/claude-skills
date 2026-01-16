---
name: repo-logo-generator
description: Generate contextual logos for GitHub repositories by analyzing README content and project metadata. Use when asked to "generate a logo", "create repo logo", "make a project logo", or when a project needs visual branding.
license: MIT
compatibility: python 3.8+, requests
metadata:
  author: tsilva
  version: "1.0.1"
---

# Repo Logo Generator

Generate professional logos for GitHub repositories by analyzing project context and applying visual metaphors.

## Quick Start

```bash
# Auto-detect project and generate logo
python plugins/repo-logo-generator/skills/repo-logo-generator/scripts/repo_logo_generator.py generate \
  --output /absolute/path/to/logo.png

# Analyze project first (preview without generating)
python plugins/repo-logo-generator/skills/repo-logo-generator/scripts/repo_logo_generator.py analyze

# With specific README
python plugins/repo-logo-generator/skills/repo-logo-generator/scripts/repo_logo_generator.py generate \
  --readme /path/to/README.md \
  --output /absolute/path/to/logo.png

# Manual overrides
python plugins/repo-logo-generator/skills/repo-logo-generator/scripts/repo_logo_generator.py generate \
  --project-name "MyTool" \
  --project-type "cli" \
  --style "minimalist" \
  --output /absolute/path/to/logo.png
```

## Project Type Mappings

The generator maps project types to visual metaphors:

| Type | Visual Metaphor | Style Notes |
|------|-----------------|-------------|
| cli | Origami transformation | Geometric, clean lines |
| library | Interconnected building blocks | Modular, structured |
| webapp | Modern interface window | Clean, minimal chrome |
| api | Messenger bird carrying data packet | Dynamic, flowing |
| framework | Architectural scaffold/blueprint | Solid, foundational |
| tool | Precision instrument | Functional, sharp edges |
| converter | Metamorphosis symbol (butterfly) | Transformation theme |
| runner | Sprinter in motion | Speed, energy, momentum |
| validator | Wax seal of approval | Trust, authenticity |
| linter | Elegant brush sweeping code | Refinement, polish |
| test | Test tube with checkmarks | Precision, verification |
| dashboard | Mission control panel | Overview, organized |
| analytics | Magnifying glass revealing patterns | Discovery, insight |
| default | Abstract geometric shape | Clean, professional |

## Technical Requirements

Generated logos must meet these criteria:

- **No text**: Readable at small sizes (16x16 to 256x256)
- **Centered composition**: Works in circular and square crops
- **Dark/light mode compatible**: Works on both backgrounds
- **Clean vector style**: Minimalist, not photorealistic
- **Single focal point**: One clear visual element

## CLI Reference

### `analyze` Command

Preview project analysis without generating a logo.

```bash
python scripts/repo_logo_generator.py analyze [--readme PATH] [--cwd PATH]
```

**Options:**
- `--readme PATH`: Path to README.md (auto-detects if not specified)
- `--cwd PATH`: Working directory for project detection (defaults to current)

**Output:** JSON with detected `name`, `type`, `description`, and `suggested_metaphor`.

### `generate` Command

Generate a logo for the project.

```bash
python scripts/repo_logo_generator.py generate \
  [--readme PATH] \
  [--project-name NAME] \
  [--project-type TYPE] \
  [--description DESC] \
  [--style STYLE] \
  [--model MODEL] \
  --output PATH
```

**Options:**
- `--readme PATH`: Path to README.md for context extraction
- `--project-name NAME`: Override detected project name
- `--project-type TYPE`: Override detected type (see mapping table)
- `--description DESC`: Override detected description
- `--style STYLE`: Style hint (minimalist, playful, corporate, tech)
- `--model MODEL`: OpenRouter model (default: google/gemini-2.0-flash-exp:free)
- `--output PATH`: **Required.** Absolute path for output PNG

## Custom Metaphors

For project types not in the mapping table, the generator creates custom metaphors based on:

1. Project name keywords (e.g., "fast" suggests speed imagery)
2. Description analysis for domain hints
3. File patterns (e.g., test files suggest testing tools)

Override with `--project-type` for explicit control.

## Environment

Requires `SKILL_OPENROUTER_API_KEY` environment variable.

## Examples

```bash
# CLI tool logo
python scripts/repo_logo_generator.py generate \
  --project-name "quicksort" \
  --project-type "cli" \
  --output /Users/me/quicksort/logo.png

# API service logo
python scripts/repo_logo_generator.py generate \
  --project-type "api" \
  --style "corporate" \
  --output /Users/me/myapi/assets/logo.png

# Auto-detect everything
cd /Users/me/myproject
python /path/to/scripts/repo_logo_generator.py generate --output ./logo.png
```
