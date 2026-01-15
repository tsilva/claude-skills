# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin that provides access to 300+ AI models via the OpenRouter API. It allows Claude Code to call external models (GPT-5, Gemini, Llama, Mistral, Flux, etc.) for text completion, image generation, and model discovery.

## Architecture

The plugin follows the Claude Code plugin structure:
- `plugins/openrouter/skills/openrouter/SKILL.md` - Skill definition with metadata and instructions
- `plugins/openrouter/skills/openrouter/scripts/openrouter_client.py` - Python client (single-file, no dependencies except `requests`)
- `plugins/openrouter/.claude-plugin/plugin.json` - Plugin metadata
- `.claude-plugin/marketplace.json` - Marketplace configuration

The Python client (`openrouter_client.py`) is standalone and uses only the `requests` library. It provides both CLI and programmatic interfaces through the `OpenRouterClient` class.

## Running the Client

Requires `SKILL_OPENROUTER_API_KEY` environment variable.

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

## Key Implementation Details

- The client uses OpenRouter's frontend API (`/api/frontend/models`) for model discovery to access all 600+ models including image generation models
- Automatic retry logic handles transient errors (429, 502, 503) with exponential backoff
- Image generation uses the chat completions endpoint with `modalities: ["image", "text"]`
- All image output paths must be absolute paths

## Version Management

When updating the plugin version, update these files:
- `plugins/openrouter/.claude-plugin/plugin.json` (version field)
- `.claude-plugin/marketplace.json` (version field)
- `README.md` (version badge)
