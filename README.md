<div align="center">
  <img src="logo.png" alt="Claude Skills" width="280"/>

  [![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-DA7856?style=flat&logo=anthropic)](https://claude.ai/code)
  [![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)
  [![GitHub Stars](https://img.shields.io/github/stars/tsilva/claude-skills?style=flat)](https://github.com/tsilva/claude-skills/stargazers)
  [![OpenRouter](https://img.shields.io/badge/OpenRouter-Powered-6366f1?style=flat)](https://openrouter.ai)

  **Modular skills that extend Claude Code with specialized capabilities**

  [Documentation](CLAUDE.md) · [Skills Marketplace](#installation)
</div>

---

## Why Claude Skills?

- **300+ AI models at your fingertips** - Call GPT-5, Gemini, Llama, or any OpenRouter model directly from Claude Code
- **Professional READMEs in seconds** - Auto-generate documentation following GitHub best practices
- **Custom logos on demand** - Create minimalist repo logos with AI image generation
- **Security auditing built-in** - Automatically identify and clean up dangerous or redundant permissions
- **Plug and play** - Install only what you need, each skill works independently

## Available Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [OpenRouter](#openrouter) | Access 300+ AI models for text completion and image generation | 1.1.0 |
| [README Generator](#readme-generator) | Create cutting-edge README files with badges and visual hierarchy | 1.0.5 |
| [Repo Logo Generator](#repo-logo-generator) | Generate minimalist logos optimized for GitHub | 2.0.3 |
| [Settings Cleaner](#settings-cleaner) | Audit and optimize Claude Code permission whitelists | 1.1.0 |

## Installation

### Via Claude Code Marketplace

```bash
# Add the skills marketplace
/plugin marketplace add tsilva/claude-skills

# Install individual skills
/plugin install openrouter
/plugin install readme-generator
/plugin install repo-logo-generator
/plugin install settings-cleaner
```

### Manual Installation

```bash
git clone https://github.com/tsilva/claude-skills.git
cd claude-skills
./scripts/install-hooks.sh  # Optional: auto-bump versions on changes
```

## Quick Start

### Environment Setup

```bash
export SKILL_OPENROUTER_API_KEY="sk-or-..."  # Get key at https://openrouter.ai/keys
```

### Text Completion

```bash
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py chat \
  "openai/gpt-5.2" "Explain quantum computing in one paragraph"
```

### Image Generation

```bash
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image \
  "google/gemini-3-pro-image-preview" "A futuristic city at sunset" \
  --output /path/to/output.png
```

### Logo Generation

```bash
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image \
  "google/gemini-3-pro-image-preview" \
  "A minimalist logo for MyProject: geometric terminal icon. Clean vector style on solid #0d1117 background. White icon, no text." \
  --output /path/to/logo.png
```

---

## Skills

### OpenRouter

<p>
  <a href="https://openrouter.ai"><img src="https://img.shields.io/badge/OpenRouter-Powered-6366f1?style=flat" alt="OpenRouter"></a>
  <img src="https://img.shields.io/badge/Version-1.1.0-green?style=flat" alt="Version">
  <img src="https://img.shields.io/badge/Models-300+-purple?style=flat" alt="300+ Models">
</p>

Gateway to 300+ AI models through a unified API. Call any model from OpenAI, Anthropic, Google, Meta, Mistral, and more.

#### Commands

```bash
# Text completion
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py chat MODEL "prompt"

# Image generation (use absolute paths)
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image MODEL "description" --output /path/output.png

# Model discovery
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py models [vision|image_gen|tools|long_context]
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py find "search term"
```

#### Popular Models

| Use Case | Model ID | Notes |
|----------|----------|-------|
| General | `openai/gpt-5.2` | Fast, capable |
| Reasoning | `anthropic/claude-opus-4.5` | SOTA reasoning |
| Code | `anthropic/claude-sonnet-4.5` | Great for code |
| Long context | `google/gemini-3-flash-preview` | 1M+ tokens, cheap |
| Image gen | `google/gemini-3-pro-image-preview` | Fast, affordable |
| Image gen | `black-forest-labs/flux.2-pro` | High quality |

#### Python Usage

```python
import sys
sys.path.insert(0, "plugins/openrouter/skills/openrouter/scripts")
from openrouter_client import OpenRouterClient
import os

client = OpenRouterClient(os.environ["SKILL_OPENROUTER_API_KEY"])
response = client.chat_simple("anthropic/claude-sonnet-4.5", "Hello!")
```

[Full documentation](plugins/openrouter/skills/openrouter/SKILL.md)

---

### README Generator

<p>
  <img src="https://img.shields.io/badge/Version-1.0.5-green?style=flat" alt="Version">
  <img src="https://img.shields.io/badge/OpenRouter-Integration-6366f1?style=flat" alt="OpenRouter Integration">
</p>

Create READMEs that hook readers in 5 seconds, prove value in 30 seconds, and enable success in under 10 minutes.

#### Framework: Hook -> Prove -> Enable -> Extend

| Phase | Time | Purpose |
|-------|------|---------|
| **Hook** | 0-5 sec | Logo + badges + one-liner |
| **Prove** | 5-30 sec | Features + social proof |
| **Enable** | 30s - 10m | Install + working example |
| **Extend** | Committed | Docs + contributing |

#### Features

- **Smart analysis** - Auto-detects project type, language, framework
- **Modern design** - Centered hero, badge collections, visual hierarchy
- **Logo integration** - Works with repo-logo-generator skill
- **Best practices** - Follows GitHub README conventions

[Full documentation](plugins/readme-generator/skills/readme-generator/SKILL.md)

---

### Repo Logo Generator

<p>
  <img src="https://img.shields.io/badge/Version-2.0.3-green?style=flat" alt="Version">
  <img src="https://img.shields.io/badge/OpenRouter-Integration-6366f1?style=flat" alt="OpenRouter Integration">
</p>

Generate professional minimalist logos optimized for GitHub's dark theme.

#### Prompt Template

```
A minimalist logo for {PROJECT_NAME}: {VISUAL_METAPHOR}.
Clean vector style on solid #0d1117 background.
Bright, light-colored icon. No text, no letters.
Single centered icon, geometric shapes, works at 64x64px.
```

#### Visual Metaphors

| Project Type | Metaphor |
|--------------|----------|
| CLI tool | Geometric terminal, origami |
| Library | Interconnected blocks |
| Web app | Modern interface window |
| API | Messenger bird with data |
| Framework | Architectural scaffold |

#### Example

```bash
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image \
  "google/gemini-3-pro-image-preview" \
  "A minimalist logo for fastgrep: magnifying glass with speed lines. Clean vector on #0d1117 background. White icon, no text." \
  --output /path/to/logo.png
```

[Full documentation](plugins/repo-logo-generator/skills/repo-logo-generator/SKILL.md)

---

### Settings Cleaner

<p>
  <img src="https://img.shields.io/badge/Version-1.0.0-green?style=flat" alt="Version">
  <img src="https://img.shields.io/badge/Security-Audit-red?style=flat" alt="Security">
</p>

Audit and optimize Claude Code permission whitelists by identifying dangerous patterns, overly specific approvals, and redundant entries.

#### What It Checks

| Category | Description | Example |
|----------|-------------|---------|
| 🔴 **Dangerous** | Overly broad permissions | `Bash(*:*)`, `Read(/*)`, `Skill(*)` |
| 🟡 **Specific** | Hardcoded arguments | `Bash(python test.py)` → `Bash(python:*)` |
| 🔵 **Redundant** | Covered by broader permission | Project has `Bash(ls -la)`, global has `Bash(ls:*)` |
| ✅ **Good** | Well-scoped permissions | `Bash(pytest:*)`, `Read(/Users/name/*)` |

**New in v1.1.0**: Self-awareness detection - the tool now detects when it's analyzing its own permissions and provides guidance on whether to retain them.

#### Commands

```bash
# Analyze permissions (read-only)
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with colorama plugins/settings-cleaner/skills/settings-cleaner/scripts/settings_cleaner.py analyze

# Interactive cleanup with confirmations
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with colorama plugins/settings-cleaner/skills/settings-cleaner/scripts/settings_cleaner.py clean

# Auto-fix redundant permissions only (safest)
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with colorama plugins/settings-cleaner/skills/settings-cleaner/scripts/settings_cleaner.py auto-fix
```

#### Safety Features

- **Automatic backups** - Creates `.bak` files before any modifications
- **Interactive mode** - Prompts for each dangerous/specific pattern
- **Auto-fix safety** - Only removes redundancies (no dangerous changes)
- **Color-coded output** - Clear visual categorization of issues

#### Usage from Claude Code

Simply ask:
- "Clean up my settings"
- "Review my permissions"
- "Audit my security settings"

[Full documentation](plugins/settings-cleaner/skills/settings-cleaner/SKILL.md)

---

## Repository Structure

```
claude-skills/
├── plugins/
│   ├── openrouter/              # OpenRouter skill (v1.1.0)
│   ├── readme-generator/        # README Generator skill (v1.0.5)
│   ├── repo-logo-generator/     # Logo Generator skill (v2.0.3)
│   └── settings-cleaner/        # Settings Cleaner skill (v1.1.0)
├── hooks/
│   └── pre-commit               # Auto-version bump hook
├── scripts/
│   ├── bump-version.py          # Version management
│   └── install-hooks.sh         # Hook installer
├── .claude-plugin/
│   └── marketplace.json         # Plugin registry
├── logo.png                     # Repository logo
├── CLAUDE.md                    # Developer documentation
└── README.md                    # This file
```

## Adding New Skills

See [CLAUDE.md](CLAUDE.md#adding-a-new-skill) for step-by-step instructions on creating skills.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-skill`)
3. Add your skill following the structure in [CLAUDE.md](CLAUDE.md)
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgements

- **[Claude Code](https://claude.ai/code)** - AI-powered development by Anthropic
- **[OpenRouter](https://openrouter.ai)** - Unified API for 300+ AI models
- **[shields.io](https://shields.io)** - Badge generation service

---

<p align="center">
  Made with Claude Code
</p>
