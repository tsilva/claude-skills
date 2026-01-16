# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code skills repository containing multiple modular plugins. Each skill provides specialized capabilities through the Claude Code plugin system. Skills are organized as independent plugins with their own versioning.

## Repository Architecture

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json         # Lists all available plugins
├── plugins/
│   └── {plugin-name}/           # One directory per plugin
│       ├── .claude-plugin/
│       │   └── plugin.json      # Plugin metadata (name, version, author)
│       └── skills/
│           └── {skill-name}/    # Skill definition
│               ├── SKILL.md     # Skill instructions and metadata (required)
│               ├── scripts/     # Executable code (optional)
│               ├── references/  # Documentation loaded on-demand (optional)
│               └── assets/      # Static resources like templates, icons (optional)
├── CLAUDE.md                    # This file
└── README.md                    # Repository documentation
```

### Design Principles

1. **One plugin per skill**: Each skill is a self-contained plugin with independent versioning
2. **Minimal dependencies**: Scripts should be standalone with minimal external dependencies
3. **Absolute paths**: All file operations should use absolute paths
4. **Environment variables**: API keys use `SKILL_{SKILLNAME}_API_KEY` convention

## Available Skills

### OpenRouter

Provides access to 300+ AI models via the OpenRouter API.

**Key files:**
- `plugins/openrouter/skills/openrouter/SKILL.md` - Skill definition
- `plugins/openrouter/skills/openrouter/scripts/openrouter_client.py` - Python client (single-file, uses only `requests`)
- `plugins/openrouter/.claude-plugin/plugin.json` - Plugin metadata

**Environment variable:** `SKILL_OPENROUTER_API_KEY`

**Usage:**
```bash
# Text completion
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py chat MODEL "prompt"

# Image generation (use absolute paths)
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image MODEL "description" --output /absolute/path/output.png

# List models by capability
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py models [vision|image_gen|tools|long_context]

# Search models
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py find "search term"
```

**Key implementation details:**
- Uses OpenRouter's frontend API (`/api/frontend/models`) to access all 600+ models including image generation models
- Automatic retry logic handles transient errors (429, 502, 503) with exponential backoff
- Image generation uses the chat completions endpoint with `modalities: ["image", "text"]`

### README Generator

Creates cutting-edge README files with modern design patterns and optional AI-generated logos.

**Key files:**
- `plugins/readme-generator/skills/readme-generator/SKILL.md` - Skill definition
- `plugins/readme-generator/.claude-plugin/plugin.json` - Plugin metadata

**Features:**
- Smart project analysis (auto-detects language, framework, package manager)
- Modern README structure with centered hero, badges, and visual hierarchy
- Logo generation integration with OpenRouter image models
- Best practices for GitHub READMEs (accessibility, mobile-friendly, scannable)

**Logo generation with OpenRouter:**
```bash
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image \
  "google/gemini-3-pro-image-preview" \
  "A minimalist logo for [PROJECT]: [concept]. Clean vector style, no text." \
  --output /absolute/path/assets/logo.png
```

## Adding a New Skill

### Step 1: Create Plugin Structure

```bash
mkdir -p plugins/{plugin-name}/.claude-plugin
mkdir -p plugins/{plugin-name}/skills/{skill-name}/scripts
```

### Step 2: Create Plugin Metadata

Create `plugins/{plugin-name}/.claude-plugin/plugin.json`:
```json
{
  "name": "{plugin-name}",
  "description": "Brief description of what this skill does.",
  "version": "1.0.0",
  "author": {
    "name": "your-name"
  }
}
```

### Step 3: Create Skill Definition

Create `plugins/{plugin-name}/skills/{skill-name}/SKILL.md`:
```markdown
---
name: {skill-name}
description: What the skill does and when to use it. Use third person. Include trigger phrases like "Use when..." or "Triggers on requests like...".
license: MIT
compatibility: python 3.8+
metadata:
  author: your-name
  version: "1.0.0"
---

# {Skill Title}

Skill instructions and documentation...
```

See the **SKILL.md Specification** section below for field constraints and best practices.

### Step 4: Register in Marketplace

Add entry to `.claude-plugin/marketplace.json`:
```json
{
  "name": "{plugin-name}",
  "source": "./plugins/{plugin-name}",
  "description": "Same description as plugin.json",
  "version": "1.0.0"
}
```

### Step 5: Update Permissions (if needed)

Add to `.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": [
      "Skill({skill-name})"
    ]
  }
}
```

## SKILL.md Specification

Based on the official [Agent Skills Specification](https://agentskills.io/specification).

### Required Frontmatter Fields

| Field | Constraints |
|-------|-------------|
| `name` | Max 64 chars. Lowercase letters, numbers, hyphens only. Must match parent directory name. Cannot contain "anthropic" or "claude". |
| `description` | Max 1024 chars. Non-empty. Must be in **third person**. Should describe what the skill does AND when to use it (triggers). |

### Optional Frontmatter Fields

| Field | Purpose |
|-------|---------|
| `license` | Must be `MIT` for all skills in this repository |
| `compatibility` | Max 500 chars. Environment requirements (python version, packages, etc.) |
| `metadata` | Key-value mapping for author, version, and custom properties |
| `allowed-tools` | Space-delimited list of pre-approved tools (experimental) |

### Description Best Practices

The description is the **primary triggering mechanism**. Claude uses it to decide when to activate a skill from potentially 100+ available skills.

**Good description:**
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Bad description:**
```yaml
description: Helps with documents
```

### Directory Structure

```
skill-name/
├── SKILL.md          # Required - skill instructions and metadata
├── scripts/          # Executable code (Python, Bash, etc.)
├── references/       # Documentation loaded on-demand
└── assets/           # Static resources (templates, icons, fonts)
```

- **scripts/**: Code Claude can run without loading into context. Token-efficient.
- **references/**: Detailed docs Claude reads only when needed. Keep one level deep from SKILL.md.
- **assets/**: Files for output (not loaded into context).

## Best Practices

Based on official [Anthropic skill authoring guidelines](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

### Conciseness is Key

Claude is already smart. Only add context Claude doesn't already have.

- Challenge each piece: "Does Claude really need this?"
- Prefer concise examples over verbose explanations
- Keep SKILL.md body **under 500 lines**

### Progressive Disclosure

Skills use 3-tier loading to minimize context usage:

1. **Metadata** (~100 tokens): `name` and `description` loaded at startup
2. **SKILL.md body** (<5000 tokens): Loaded when skill triggers
3. **Bundled resources** (as needed): Loaded on-demand from scripts/, references/, assets/

### Writing Instructions

- Use **imperative/infinitive form** (e.g., "Extract text..." not "This extracts text...")
- Keep file references **one level deep** from SKILL.md
- Structure files >100 lines with a **table of contents**
- Avoid time-sensitive information

### Scripts Guidelines

- Bundle scripts for **deterministic operations** that Claude would otherwise rewrite
- Scripts should **solve problems, not punt** to Claude
- Document all "magic numbers" with comments explaining the value
- Include helpful error messages that guide resolution

### Testing

Test skills with all models you plan to use:
- **Haiku**: Does the skill provide enough guidance?
- **Sonnet**: Is the skill clear and efficient?
- **Opus**: Does the skill avoid over-explaining?

## Version Management

**Every time a SKILL.md file is modified, you MUST bump the version in ALL three locations:**

1. `plugins/{plugin-name}/skills/{skill-name}/SKILL.md` - `metadata.version` in frontmatter
2. `plugins/{plugin-name}/.claude-plugin/plugin.json` - `version` field
3. `.claude-plugin/marketplace.json` - `version` field for that plugin

**Why:** The version number is how skill updates are detected. If you don't bump the version, changes won't be picked up.

Also review and update `README.md` if needed (version in skills table, feature descriptions, usage examples).

**Critical:** All three version numbers MUST be identical. Before committing, verify synchronization.

## Conventions

- **Skill names**: lowercase, hyphenated (e.g., `openrouter`, `code-review`). Max 64 chars.
- **Plugin names**: typically match skill name for single-skill plugins
- **API keys**: `SKILL_{SKILLNAME_UPPERCASE}_API_KEY`
- **Scripts**: Place in `scripts/` subdirectory
  - Prefer single-file with minimal dependencies
  - Use `#!/usr/bin/env python3` shebang for portability
  - Include docstrings explaining purpose and usage
  - Handle errors gracefully with helpful messages
- **References**: Place in `references/` subdirectory for detailed documentation
- **Assets**: Place in `assets/` subdirectory for templates, icons, and static files
