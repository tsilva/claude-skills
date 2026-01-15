---
name: openrouter
description: Invoke 300+ AI models via OpenRouter API for multi-step workflows. Use when Claude Code needs to call external models (GPT-4, Gemini, Llama, Mistral, etc.) for text completion, image generation, or model discovery. Triggers on requests like "use OpenRouter to...", "call GPT-4 to...", "generate an image with Gemini", or when delegating tasks to other AI models.
---

# OpenRouter

Gateway to 300+ AI models through a unified API. Requires `OPENROUTER_API_KEY` environment variable.

## Setup

```bash
export OPENROUTER_API_KEY="sk-or-..."  # Get key at https://openrouter.ai/keys
```

## Quick Reference

**Text completion:**
```bash
python scripts/openrouter_client.py chat MODEL "prompt" [--system "sys"] [--max-tokens N] [--temperature T]
```

**Image generation:**
```bash
python scripts/openrouter_client.py image MODEL "description" [--output file.png] [--aspect 16:9] [--size 2K]
```

**Model discovery:**
```bash
python scripts/openrouter_client.py models [vision|image_gen|tools|long_context]
python scripts/openrouter_client.py find "search term"
```

## Common Models

| Use Case | Model ID | Notes |
|----------|----------|-------|
| General | `anthropic/claude-3.5-sonnet` | Fast, capable |
| Reasoning | `openai/gpt-4o` | Strong reasoning |
| Code | `deepseek/deepseek-coder` | Code specialist |
| Long docs | `google/gemini-1.5-pro` | 1M context |
| Image gen | `google/gemini-2.5-flash-image` | Fast, cheap |
| Image gen | `black-forest-labs/flux.2-pro` | High quality |

## Multi-Step Workflow Patterns

### Pattern 1: Sequential Model Chain
Call multiple models in sequence, passing outputs forward:

```python
# Step 1: Generate outline with one model
outline = client.chat_simple("openai/gpt-4o", "Create outline for: {topic}")

# Step 2: Expand with another model
content = client.chat_simple("anthropic/claude-3.5-sonnet", f"Expand this outline:\n{outline}")
```

### Pattern 2: Parallel Model Comparison
Get responses from multiple models for comparison:

```bash
# Run these in parallel
python scripts/openrouter_client.py chat openai/gpt-4o "Explain X" > gpt4_response.txt &
python scripts/openrouter_client.py chat anthropic/claude-3.5-sonnet "Explain X" > claude_response.txt &
wait
```

### Pattern 3: Specialized Delegation
Route specific tasks to specialized models:

```bash
# Use code model for code tasks
python scripts/openrouter_client.py chat deepseek/deepseek-coder "Write a function to..."

# Use vision model for image analysis
python scripts/openrouter_client.py chat google/gemini-1.5-pro "Analyze this image: [base64]"

# Use image model for generation
python scripts/openrouter_client.py image google/gemini-2.5-flash-image "A cyberpunk city" -o city.png
```

### Pattern 4: Structured Output Pipeline
Request JSON for programmatic processing:

```bash
# Get structured data
python scripts/openrouter_client.py chat openai/gpt-4o "Extract entities from: {text}" --json > entities.json

# Process the JSON in next step
```

## Image Generation

**Required:** Use chat completions endpoint with `modalities: ["image", "text"]`

**Aspect ratios:** `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `21:9`
**Sizes:** `1K`, `2K`, `4K`

```bash
# Generate landscape image
python scripts/openrouter_client.py image google/gemini-2.5-flash-image \
  "Mountain sunset with dramatic clouds" \
  --output mountain.png --aspect 16:9 --size 2K
```

## Error Handling

The script handles retries automatically for transient errors (429, 502, 503).

**Common errors:**
- `401`: Invalid API key - check `OPENROUTER_API_KEY`
- `402`: Add credits at openrouter.ai
- `429`: Rate limited - script auto-retries

## Python Usage (Direct Import)

For complex workflows, import the client directly:

```python
import sys
sys.path.insert(0, "scripts")
from openrouter_client import OpenRouterClient
import os

client = OpenRouterClient(os.environ["OPENROUTER_API_KEY"])

# Simple chat
response = client.chat_simple("anthropic/claude-3.5-sonnet", "Hello!")

# Full chat with history
result = client.chat("openai/gpt-4o", [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Explain recursion"},
    {"role": "assistant", "content": "Recursion is..."},
    {"role": "user", "content": "Give an example"}
])
content = result["choices"][0]["message"]["content"]

# Generate image
images = client.generate_image(
    "google/gemini-2.5-flash-image",
    "A serene forest path",
    output_path="forest.png",
    aspect_ratio="16:9"
)

# Find models
vision_models = client.list_models("vision")
claude_models = client.find_model("claude")
```
