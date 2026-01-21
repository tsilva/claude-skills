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
├── scripts/
│   ├── bump-version.py          # Version bumping CLI tool
│   └── validate_skills.py       # Skill validation against spec
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
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py chat MODEL "prompt"

# Image generation (use absolute paths)
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image MODEL "description" --output /absolute/path/output.png

# List models by capability
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py models [vision|image_gen|tools|long_context]

# Search models
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py find "search term"
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
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image \
  "google/gemini-3-pro-image-preview" \
  "A minimalist logo for [PROJECT]: [concept]. Clean vector style, no text." \
  --output /absolute/path/assets/logo.png
```

**Logo configuration:** Logo appearance is customizable via JSON config files. The system checks in order (first found wins):
1. `./.claude/readme-generator.json` (project level)
2. `~/.claude/readme-generator.json` (user level)
3. `assets/default-config.json` (bundled with repo-logo-generator skill)

Example config:
```json
{
  "logo": {
    "background": "#1a1b26",
    "iconColors": ["#7aa2f7", "#bb9af7", "#7dcfff"],
    "style": "geometric",
    "model": "google/gemini-3-pro-image-preview"
  }
}
```

See `repo-logo-generator` SKILL.md for all configurable parameters.

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

### Step 6: Validate

**Always run validation after adding or modifying any skill:**
```bash
python scripts/validate_skills.py
```

This validates against the [Agent Skills specification](https://agentskills.io/specification) and repository rules. Fix any errors before committing.

**Important:** After modifying any SKILL.md file, Claude must bump the version. See the **Version Management** section below for the workflow.

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
| `argument-hint` | Shows in autocomplete what arguments the slash command expects (e.g., `[issue-number]`, `[analyze\|clean\|auto-fix]`) |
| `disable-model-invocation` | Set to `true` to only allow manual `/name` invocation. Prevents Claude from auto-triggering. Defaults to `false` |
| `user-invocable` | Set to `false` to hide from `/` menu. Claude can still use it automatically. Defaults to `true` |

### Slash Commands

In Claude Code, **every skill automatically becomes a slash command** based on its `name` field. For example, a skill with `name: readme-generator` can be invoked as `/readme-generator`.

**How it works:**
- The `name` field becomes the slash command (e.g., `name: my-skill` → `/my-skill`)
- Users can type `/skill-name [arguments]` to manually invoke the skill
- Claude can also invoke skills automatically based on their `description` (unless `disable-model-invocation: true`)

**Slash command fields:**
```yaml
---
name: settings-cleaner
description: Analyzes and cleans up Claude Code permission whitelists...
argument-hint: "[analyze|clean|auto-fix]"     # Shows users what arguments they can pass
disable-model-invocation: false               # Allow both manual and auto invocation
user-invocable: true                          # Show in slash command menu (default)
---
```

**Examples of slash command usage:**
- `/readme-generator` - Generate a README for the current project
- `/readme-generator ./my-project` - Generate README for a specific path
- `/settings-cleaner analyze` - Run settings analysis
- `/repo-logo-generator minimalist` - Generate a logo with style preference

**Passing arguments:**
When users invoke `/skill-name arg1 arg2`, the arguments are available in the skill as `$ARGUMENTS`. If the skill doesn't reference `$ARGUMENTS`, Claude Code automatically appends the arguments to the skill instructions.

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

## Dependency Management Best Practices

Following official Agent Skills specification and Anthropic recommendations.

### Gold Standard: UV with Inline Dependencies

All scripts use UV with inline dependency declarations:
```bash
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests scripts/openrouter_client.py ...
```

**Why UV is preferred:**
- Zero setup for users (no pip install needed)
- Dependencies declared inline (PEP 723 standard)
- Automatic caching and fast execution
- Full portability across systems
- Official Anthropic/Claude Code recommendation

### Handling Missing Dependencies

Scripts validate dependencies at import with helpful error messages:
```python
try:
    import requests
except ImportError:
    print("Error: requests library required.", file=sys.stderr)
    print("Run with: uv run --with requests <script>", file=sys.stderr)
    sys.exit(1)
```

**Pattern:**
- Print to `stderr` (not stdout)
- Exit with code 1
- Provide exact recovery command
- Name the specific missing library

### macOS Sandbox Limitation

UV accesses `SystemConfiguration.framework` APIs for proxy detection, which requires `dangerouslyDisableSandbox: true` on macOS. This is a known UV limitation, not a skill design issue.

**Expected behavior:**
- On first execution, Claude may attempt with sandbox enabled
- If it fails with system-configuration errors, Claude will retry with sandbox disabled
- This is normal and does not indicate a security problem

**Fallback:** For restricted environments, users can pre-install dependencies and use plain Python:
```bash
python3 -m pip install requests
python3 /absolute/path/to/script.py ...
```

However, the UV approach is strongly preferred for its portability and zero-setup benefits.

### Optional Dependencies

For non-critical dependencies, use graceful degradation:
```python
try:
    from colorama import Fore, Style
    HAS_COLOR = True
except ImportError:
    # Fallback: no colors
    class Fore:
        RED = GREEN = ""
    HAS_COLOR = False
```

This allows the script to function even when optional packages are unavailable.

## Version Management

Claude is responsible for version bumping. **After modifying any SKILL.md file**, Claude must:

1. **Check if version already bumped**: If the file is uncommitted and the version line already changed, skip bumping
2. **Determine bump type** based on changes made (see strategy below)
3. **Run the bump script** to update all 3 version locations
4. **Run validation** to verify sync

### Version Bump Strategy

| Bump Type | When to Use | Example Changes |
|-----------|-------------|-----------------|
| **Patch** (X.Y.Z+1) | Documentation, typos, clarifications, bug fixes | Fix typo in instructions, clarify wording |
| **Minor** (X.Y+1.0) | New features, new parameters, enhanced capabilities | Add new command, add optional feature |
| **Major** (X+1.0.0) | Breaking changes, removed features, changed behavior | Remove parameter, change default behavior |

### Version Bump Commands

```bash
# Check if version already bumped (returns 0 if bumped, 1 if not)
python scripts/bump-version.py {plugin-name} --check-uncommitted

# Preview what version would be (dry run)
python scripts/bump-version.py {plugin-name} --type {patch|minor|major} --dry-run

# Apply version bump
python scripts/bump-version.py {plugin-name} --type {patch|minor|major}

# Validate all skills (always run after version changes)
python scripts/validate_skills.py
```

### Workflow

When Claude modifies a SKILL.md file:

1. **After editing**, check if version needs bumping:
   ```bash
   python scripts/bump-version.py {plugin-name} --check-uncommitted
   ```
   - Exit 0 = version already bumped, skip to validation
   - Exit 1 = version not bumped, continue to step 2

2. **Determine bump type** based on the changes:
   - Documentation/typo/clarification → `patch`
   - New feature/capability → `minor`
   - Breaking change → `major`

3. **Apply the bump**:
   ```bash
   python scripts/bump-version.py {plugin-name} --type {type}
   ```

4. **Always validate**:
   ```bash
   python scripts/validate_skills.py
   ```

### Version Locations (Auto-Synchronized)

The bump script updates all three locations:

1. `plugins/{plugin}/skills/{skill}/SKILL.md` - `metadata.version`
2. `plugins/{plugin}/.claude-plugin/plugin.json` - `version`
3. `.claude-plugin/marketplace.json` - `version` for that plugin

**Why versions matter:** The version number is how skill updates are detected. If the version doesn't change, updates won't be picked up.

**Note:** Also review and update `README.md` if needed (version in skills table, feature descriptions, usage examples). This is not automated.

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
