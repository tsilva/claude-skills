# OpenRouter Skill for Claude Code

A Claude Code skill that provides access to 300+ AI models via the [OpenRouter](https://openrouter.ai) API.

## Features

- **Text Completion**: Call any model (GPT-4, Claude, Gemini, Llama, Mistral, etc.)
- **Image Generation**: Generate images with models like Gemini Flash, Flux, and more
- **Model Discovery**: Search and filter models by capability (vision, tools, long context)
- **Multi-Step Workflows**: Chain models together for complex tasks

## Installation

```bash
# Add the marketplace
/plugin marketplace add tsilva/agent-skill-openrouter

# Install the plugin
/plugin install openrouter
```

## Setup

Set your OpenRouter API key:

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

Get your API key at [openrouter.ai/keys](https://openrouter.ai/keys)

## License

MIT
