<p align="center">
  <img src="assets/logo.png" alt="OpenRouter Skill Logo" width="200" height="200">
</p>

<h1 align="center">OpenRouter Skill for Claude Code</h1>

<p align="center">
  <strong>Gateway to 300+ AI models through a unified API</strong>
</p>

<p align="center">
  <a href="https://openrouter.ai"><img src="https://img.shields.io/badge/Powered%20by-OpenRouter-6366f1?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgZmlsbD0id2hpdGUiLz48L3N2Zz4=" alt="OpenRouter"></a>
  <a href="https://claude.ai/code"><img src="https://img.shields.io/badge/Built%20with-Claude%20Code-DA7857?logo=anthropic" alt="Claude Code"></a>
  <a href="https://github.com/tsilva/agent-skill-openrouter"><img src="https://img.shields.io/badge/GitHub-tsilva%2Fagent--skill--openrouter-blue?logo=github" alt="GitHub"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python"></a>
  <img src="https://img.shields.io/badge/Version-1.0.3-green" alt="Version">
  <img src="https://img.shields.io/badge/Models-300%2B-purple" alt="300+ Models">
</p>

---

## Overview

A Claude Code plugin that provides seamless access to **300+ AI models** via the [OpenRouter](https://openrouter.ai) API. It allows Claude Code to call external models including GPT-4, Gemini, Llama, Mistral, Flux, and many more.

Whether you need to generate images, leverage specialized coding models, or compare outputs from multiple AI providers, this plugin provides a unified interface for all your AI model needs directly within Claude Code.

## Features

| Feature | Description |
|---------|-------------|
| **Text Completion** | Call any model (GPT-4, Claude, Gemini, Llama, Mistral, etc.) |
| **Image Generation** | Generate images with Flux, Gemini Flash, and other image models |
| **Model Discovery** | Search and filter models by capability (vision, tools, long context) |
| **Model Chaining** | Chain models together for complex tasks |
| **Automatic Retries** | Built-in retry logic for rate limits and transient errors |

## Installation

### Via Claude Code Plugin Marketplace

```bash
# Add the marketplace
/plugin marketplace add tsilva/agent-skill-openrouter

# Install the plugin
/plugin install openrouter
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/tsilva/agent-skill-openrouter.git

# Navigate to the plugin directory
cd agent-skill-openrouter
```

## Setup

Set your OpenRouter API key as an environment variable:

```bash
export SKILL_OPENROUTER_API_KEY="sk-or-..."
```

Get your API key at [openrouter.ai/keys](https://openrouter.ai/keys)

## Quick Reference

### Text Completion

```bash
python scripts/openrouter_client.py chat MODEL "prompt" [--system "sys"] [--max-tokens N] [--temperature T]
```

### Image Generation

```bash
python scripts/openrouter_client.py image MODEL "description" [--output /absolute/path/file.png] [--aspect 16:9] [--size 2K]
```

### Model Discovery

```bash
# List models by capability
python scripts/openrouter_client.py models [vision|image_gen|tools|long_context]

# Search for specific models
python scripts/openrouter_client.py find "search term"
```

## Common Models

| Use Case | Model ID | Notes |
|----------|----------|-------|
| General | `openai/gpt-5.2` | Fast, capable |
| Reasoning | `anthropic/claude-opus-4.5` | SOTA reasoning |
| Code | `anthropic/claude-sonnet-4.5` | Simple code |
| Long docs | `google/gemini-3-flash-preview` | Long context, cheap |
| Image gen | `google/gemini-3-pro-image-preview` | Fast, cheap |
| Image gen | `black-forest-labs/flux.2-pro` | High quality |

## Usage Patterns

### Sequential Model Chain

Call multiple models in sequence, passing outputs forward:

```python
# Step 1: Generate outline with one model
outline = client.chat_simple("openai/gpt-5.2", "Create outline for: {topic}")

# Step 2: Expand with another model
content = client.chat_simple("anthropic/claude-sonnet-4.5", f"Expand this outline:\n{outline}")
```

### Parallel Model Comparison

Get responses from multiple models for comparison:

```bash
# Run these in parallel
python scripts/openrouter_client.py chat openai/gpt-5.2 "Explain X" > gpt4_response.txt &
python scripts/openrouter_client.py chat anthropic/claude-sonnet-4.5 "Explain X" > claude_response.txt &
wait
```

### Specialized Delegation

Route specific tasks to specialized models:

```bash
# Use code model for code tasks
python scripts/openrouter_client.py chat anthropic/claude-sonnet-4.5 "Write a function to..."

# Use vision model for image analysis
python scripts/openrouter_client.py chat google/gemini-3-flash-preview "Analyze this image: [base64]"

# Use image model for generation
python scripts/openrouter_client.py image google/gemini-3-pro-image-preview "A cyberpunk city" -o city.png
```

## Python Usage

For complex workflows, import the client directly:

```python
import sys
sys.path.insert(0, "scripts")
from openrouter_client import OpenRouterClient
import os

client = OpenRouterClient(os.environ["SKILL_OPENROUTER_API_KEY"])

# Simple chat
response = client.chat_simple("anthropic/claude-sonnet-4.5", "Hello!")

# Full chat with history
result = client.chat("openai/gpt-5.2", [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Explain recursion"},
    {"role": "assistant", "content": "Recursion is..."},
    {"role": "user", "content": "Give an example"}
])
content = result["choices"][0]["message"]["content"]

# Generate image (use absolute path)
images = client.generate_image(
    "google/gemini-3-pro-image-preview",
    "A serene forest path",
    output_path="/absolute/path/to/forest.png",
    aspect_ratio="16:9"
)

# Find models
vision_models = client.list_models("vision")
claude_models = client.find_model("claude")
```

## Repository Structure

```
agent-skill-openrouter/
├── assets/
│   └── logo.png                    # Project logo
├── plugins/
│   └── openrouter/
│       ├── .claude-plugin/
│       │   └── plugin.json         # Plugin metadata
│       └── skills/
│           └── openrouter/
│               ├── SKILL.md        # Skill definition
│               └── scripts/
│                   └── openrouter_client.py  # Python client
├── .claude-plugin/
│   └── marketplace.json            # Marketplace configuration
├── LICENSE                         # MIT License
└── README.md                       # This file
```

## Error Handling

The script handles retries automatically for transient errors (429, 502, 503).

| Error Code | Description | Solution |
|------------|-------------|----------|
| `401` | Invalid API key | Check `SKILL_OPENROUTER_API_KEY` |
| `402` | Insufficient credits | Add credits at openrouter.ai |
| `429` | Rate limited | Script auto-retries |

## Reporting Issues

Found a bug or have a suggestion? Please report it:

[GitHub Issues](https://github.com/tsilva/agent-skill-openrouter/issues)

When reporting issues, please include:
- Description of the problem or suggestion
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Error messages (if applicable)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **[OpenRouter](https://openrouter.ai)** - Unified API for 300+ AI models
- **[Claude Code](https://claude.ai/code)** by Anthropic - AI-powered coding assistant
- **[Black Forest Labs](https://blackforestlabs.ai)** - Flux image generation models

---

<p align="center">
  Made with Claude Code
</p>
