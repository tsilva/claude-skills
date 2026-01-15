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
│               ├── SKILL.md     # Skill instructions and metadata
│               └── scripts/     # Supporting scripts (optional)
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
description: Detailed description including trigger phrases and use cases.
arguments:
  - name: arg_name
    description: What this argument does
    required: false
---

# {Skill Title}

Skill documentation and usage instructions...
```

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

## Version Management

When updating a skill version, update these files:
1. `plugins/{plugin-name}/.claude-plugin/plugin.json` - version field
2. `.claude-plugin/marketplace.json` - version field for that plugin
3. `README.md` - version in skills table

**Important:** Keep versions synchronized between `plugin.json` and `marketplace.json`.

## Conventions

- **Skill names**: lowercase, hyphenated (e.g., `openrouter`, `code-review`)
- **Plugin names**: typically match skill name for single-skill plugins
- **API keys**: `SKILL_{SKILLNAME_UPPERCASE}_API_KEY`
- **Scripts**: Place in `scripts/` subdirectory, prefer single-file with minimal dependencies
