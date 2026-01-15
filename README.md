<p align="center">
  <img src="assets/logo.png" alt="Claude Skills Logo" width="200" height="200">
</p>

<h1 align="center">Claude Skills</h1>

<p align="center">
  <strong>A collection of specialized skills for Claude Code</strong>
</p>

<p align="center">
  <a href="https://claude.ai/code"><img src="https://img.shields.io/badge/Built%20with-Claude%20Code-DA7857?logo=anthropic" alt="Claude Code"></a>
  <a href="https://github.com/tsilva/claude-skills"><img src="https://img.shields.io/badge/GitHub-tsilva%2Fclaude--skills-blue?logo=github" alt="GitHub"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

---

## Overview

A modular collection of Claude Code skills, each providing specialized capabilities through the plugin system. Each skill is an independent plugin with its own versioning.

## Available Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [OpenRouter](#openrouter) | Access 300+ AI models via OpenRouter API | 1.0.4 |

## Installation

### Via Claude Code Plugin Marketplace

```bash
# Add the marketplace
/plugin marketplace add tsilva/claude-skills

# Install a specific skill
/plugin install openrouter
```

### Manual Installation

```bash
git clone https://github.com/tsilva/claude-skills.git
cd claude-skills
```

---

## Skills

### OpenRouter

<p>
  <a href="https://openrouter.ai"><img src="https://img.shields.io/badge/Powered%20by-OpenRouter-6366f1" alt="OpenRouter"></a>
  <img src="https://img.shields.io/badge/Version-1.0.4-green" alt="Version">
  <img src="https://img.shields.io/badge/Models-300%2B-purple" alt="300+ Models">
</p>

Gateway to 300+ AI models through a unified API.

#### Setup

```bash
export SKILL_OPENROUTER_API_KEY="sk-or-..."  # Get key at https://openrouter.ai/keys
```

#### Features

| Feature | Description |
|---------|-------------|
| **Text Completion** | Call any model (GPT-4, Claude, Gemini, Llama, Mistral, etc.) |
| **Image Generation** | Generate images with Flux, Gemini Flash, and other image models |
| **Model Discovery** | Search and filter models by capability (vision, tools, long context) |
| **Model Chaining** | Chain models together for complex tasks |
| **Automatic Retries** | Built-in retry logic for rate limits and transient errors |

#### Quick Reference

```bash
# Text completion
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py chat MODEL "prompt"

# Image generation (use absolute paths)
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image MODEL "description" --output /absolute/path/output.png

# Model discovery
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py models [vision|image_gen|tools|long_context]
python plugins/openrouter/skills/openrouter/scripts/openrouter_client.py find "search term"
```

#### Common Models

| Use Case | Model ID | Notes |
|----------|----------|-------|
| General | `openai/gpt-5.2` | Fast, capable |
| Reasoning | `anthropic/claude-opus-4.5` | SOTA reasoning |
| Code | `anthropic/claude-sonnet-4.5` | Simple code |
| Long docs | `google/gemini-3-flash-preview` | Long context, cheap |
| Image gen | `google/gemini-3-pro-image-preview` | Fast, cheap |
| Image gen | `black-forest-labs/flux.2-pro` | High quality |

#### Usage Patterns

**Sequential Model Chain** - Call multiple models in sequence:
```python
outline = client.chat_simple("openai/gpt-5.2", "Create outline for: {topic}")
content = client.chat_simple("anthropic/claude-sonnet-4.5", f"Expand this outline:\n{outline}")
```

**Parallel Comparison** - Get responses from multiple models:
```bash
python scripts/openrouter_client.py chat openai/gpt-5.2 "Explain X" > gpt_response.txt &
python scripts/openrouter_client.py chat anthropic/claude-sonnet-4.5 "Explain X" > claude_response.txt &
wait
```

**Python Usage** - Import the client directly:
```python
import sys
sys.path.insert(0, "plugins/openrouter/skills/openrouter/scripts")
from openrouter_client import OpenRouterClient
import os

client = OpenRouterClient(os.environ["SKILL_OPENROUTER_API_KEY"])
response = client.chat_simple("anthropic/claude-sonnet-4.5", "Hello!")
```

[Full OpenRouter documentation](plugins/openrouter/skills/openrouter/SKILL.md)

---

## Repository Structure

```
claude-skills/
├── plugins/
│   └── openrouter/              # OpenRouter plugin
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── openrouter/
│               ├── SKILL.md
│               └── scripts/
│                   └── openrouter_client.py
├── .claude-plugin/
│   └── marketplace.json         # Lists all plugins
├── assets/
│   └── logo.png
├── CLAUDE.md                    # Developer guidance
└── README.md                    # This file
```

## Adding New Skills

See [CLAUDE.md](CLAUDE.md#adding-a-new-skill) for detailed instructions on adding new skills to this repository.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your skill following the structure in CLAUDE.md
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with Claude Code
</p>
