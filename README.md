<div align="center">
  <img src="logo.png" alt="claude-skills" width="512"/>

  # claude-skills

  [![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-DA7856?style=flat&logo=anthropic)](https://claude.ai/code)
  [![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)
  [![GitHub Stars](https://img.shields.io/github/stars/tsilva/claude-skills?style=flat)](https://github.com/tsilva/claude-skills/stargazers)

  **🔌 Supercharge Claude Code with auto-generated READMEs, custom logos, and security auditing**

  [Documentation](CLAUDE.md) · [Skills Marketplace](#installation)
</div>

---

## Why Claude Skills?

- **📝 Professional READMEs in seconds** - Auto-generate documentation following GitHub best practices
- **🎨 Custom logos on demand** - Create minimalist repo logos with AI image generation
- **🔐 Security auditing built-in** - Automatically identify and clean up dangerous or redundant permissions
- **⚡ Plug and play** - Install only what you need, each skill works independently

> **Note:** For access to 300+ AI models (GPT-5, Gemini, Llama, Mistral, etc.), use the [mcp-openrouter](https://github.com/tsilva/mcp-openrouter) MCP server.

## Available Skills

| Skill | Description | Version | Slash Command |
|-------|-------------|---------|---------------|
| [README Generator](#readme-generator) | Create cutting-edge README files with badges and visual hierarchy | 1.1.1 | `/readme-generator` |
| [Repo Logo Generator](#repo-logo-generator) | Generate logos with native transparent backgrounds (requires mcp-openrouter) | 4.0.0 | `/repo-logo-generator` |
| [Settings Optimizer](#claude-settings-optimizer) | Audit and optimize Claude Code permission whitelists | 1.0.0 | `/claude-settings-optimizer` |
| [Repo Name Generator](#repo-name-generator) | Generate creative, memorable repository names | 1.0.0 | `/repo-name-generator` |

## Installation

### Via Claude Code Marketplace

```bash
# Add the skills marketplace
/skills-discovery tsilva/claude-skills

# Or install individual skills directly
/skills-discovery readme-generator
/skills-discovery repo-logo-generator
/skills-discovery claude-settings-optimizer
```

### Manual Installation

```bash
git clone https://github.com/tsilva/claude-skills.git
cd claude-skills
git config core.hooksPath hooks  # Enable pre-commit version validation
```

## Quick Start

### Using Slash Commands

All skills are available as slash commands in Claude Code. Simply type `/` to see available commands with autocomplete:

```bash
/readme-generator              # Generate a README for the current project
/readme-generator ./my-project # Generate README for a specific path
/repo-logo-generator           # Generate a logo for your repository
/repo-logo-generator minimalist # Generate with a specific style preference
/settings-cleaner analyze      # Analyze permission whitelists
/settings-cleaner clean        # Interactive cleanup with confirmations
/settings-cleaner auto-fix     # Auto-remove redundant permissions
```

You can also ask Claude to use these skills naturally:
- "Create a README for this project" → triggers `/readme-generator`
- "Generate a logo for my repo" → triggers `/repo-logo-generator`
- "Clean up my settings" → triggers `/settings-cleaner`

### Logo Generation

Logo generation uses the [mcp-openrouter](https://github.com/tsilva/mcp-openrouter) MCP server:

1. **Generate image** via `mcp__openrouter__generate_image` with green background
2. **Apply chromakey** via the bundled script to convert green to transparent

Simply use `/repo-logo-generator` and Claude handles the workflow automatically.

---

## Skills

### README Generator

<p>
  <img src="https://img.shields.io/badge/Version-1.1.1-green?style=flat" alt="Version">
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
  <img src="https://img.shields.io/badge/Version-4.0.0-green?style=flat" alt="Version">
  <a href="https://github.com/tsilva/mcp-openrouter"><img src="https://img.shields.io/badge/Requires-mcp--openrouter-6366f1?style=flat" alt="Requires mcp-openrouter"></a>
</p>

Generate professional logos with transparent backgrounds using chromakey technology. Uses [mcp-openrouter](https://github.com/tsilva/mcp-openrouter) MCP server to generate logos with Gemini, then applies professional chromakey for smooth transparency.

#### Features

- **Chromakey transparency** - Industry-standard green screen technique eliminates halo artifacts
- **Multiple styles** - Supports minimalist, pixel art, vector, and complex designs
- **Configurable** - Customize colors, style, and model via JSON config files
- **MCP integration** - Uses mcp-openrouter for AI image generation

#### Visual Metaphors

| Project Type | Metaphor |
|--------------|----------|
| CLI tool | Geometric terminal, origami |
| Library | Interconnected blocks |
| Web app | Modern interface window |
| API | Messenger bird with data |
| Framework | Architectural scaffold |

#### Prerequisites

Requires the [mcp-openrouter](https://github.com/tsilva/mcp-openrouter) MCP server to be configured.

[Full documentation](plugins/repo-logo-generator/skills/repo-logo-generator/SKILL.md)

---

### Settings Cleaner

<p>
  <img src="https://img.shields.io/badge/Version-1.0.7-green?style=flat" alt="Version">
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
│   ├── readme-generator/        # README Generator skill (v1.1.1)
│   ├── repo-logo-generator/     # Logo Generator skill (v4.0.0)
│   ├── claude-settings-optimizer/ # Settings Optimizer skill (v1.0.0)
│   ├── repo-name-generator/     # Repo Name Generator skill (v1.0.0)
│   └── claude-skill-author/     # Skill authoring tools (validation, version bump)
├── .claude-plugin/
│   └── marketplace.json         # Plugin registry
├── logo.png                     # Repository logo
├── CLAUDE.md                    # Developer documentation
└── README.md                    # This file
```

## Dependency Management

This repository follows Agent Skills best practices using **UV for portable, zero-setup execution**:

```bash
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with pillow scripts/chromakey.py ...
```

**Benefits:**
- No environment setup required
- Dependencies declared inline (PEP 723 standard)
- Automatic caching for fast execution
- Full portability across systems

**macOS Sandbox Note:** On macOS, UV may require `dangerouslyDisableSandbox` because it accesses system configuration APIs. This is a known UV limitation.

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
- **[shields.io](https://shields.io)** - Badge generation service

---

<p align="center">
  Made with Claude Code
</p>
