---
name: openrouter
description: Invokes 300+ AI models via OpenRouter API for text completion, image generation, and model discovery. Use when delegating tasks to external models (GPT-5.2, Gemini 3, Llama, Mistral, etc.). Triggers on "use OpenRouter to...", "call GPT-5 to...", "generate an image with Gemini", or similar requests for external AI models.
license: Apache-2.0
compatibility: python 3.8+, requests library
metadata:
  author: tsilva
  version: "1.0.4"
---

# OpenRouter

Gateway to 300+ AI models through a unified API. Requires `SKILL_OPENROUTER_API_KEY` environment variable.

## Setup

```bash
export SKILL_OPENROUTER_API_KEY="sk-or-..."  # Get key at https://openrouter.ai/keys
```

## Quick Reference

**Text completion:**
```bash
python scripts/openrouter_client.py chat MODEL "prompt" [--system "sys"] [--max-tokens N] [--temperature T]
```

**Image generation:**
```bash
python scripts/openrouter_client.py image MODEL "description" [--output /absolute/path/file.png] [--aspect 16:9] [--size 2K]
```

**Model discovery:**
```bash
python scripts/openrouter_client.py models [vision|image_gen|tools|long_context]
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

### Pattern 1: Sequential Model Chain
Call multiple models in sequence, passing outputs forward:

```python
# Step 1: Generate outline with one model
outline = client.chat_simple("openai/gpt-5.2", "Create outline for: {topic}")

# Step 2: Expand with another model
content = client.chat_simple("anthropic/claude-sonnet-4.5", f"Expand this outline:\n{outline}")
```

### Pattern 2: Parallel Model Comparison
Get responses from multiple models for comparison:

```bash
# Run these in parallel
python scripts/openrouter_client.py chat openai/gpt-5.2 "Explain X" > gpt4_response.txt &
python scripts/openrouter_client.py chat anthropic/claude-sonnet-4.5 "Explain X" > claude_response.txt &
wait
```

### Pattern 3: Specialized Delegation
Route specific tasks to specialized models:

```bash
# Use code model for code tasks
python scripts/openrouter_client.py chat anthropic/claude-sonnet-4.5 "Write a function to..."

# Use vision model for image analysis
python scripts/openrouter_client.py chat google/gemini-3-flash-preview "Analyze this image: [base64]"

# Use image model for generation
python scripts/openrouter_client.py image google/gemini-3-pro-image-preview "A cyberpunk city" -o city.png
```

### Pattern 4: Structured Output Pipeline
Request JSON for programmatic processing:

```bash
# Get structured data
python scripts/openrouter_client.py chat openai/gpt-5.2 "Extract entities from: {text}" --json > entities.json

# Process the JSON in next step
```

## Image Generation

**Required:** Use chat completions endpoint with `modalities: ["image", "text"]`

**Aspect ratios:** `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `21:9`
**Sizes:** `1K`, `2K`, `4K`

```bash
# Generate landscape image (use absolute path for --output)
python scripts/openrouter_client.py image google/gemini-3-pro-image-preview \
  "Mountain sunset with dramatic clouds" \
  --output /absolute/path/to/mountain.png --aspect 16:9 --size 2K
```

**Note:** Always use absolute paths for `--output` to ensure images are saved to the correct location. The script creates parent directories automatically if they don't exist.

## Error Handling

The script handles retries automatically for transient errors (429, 502, 503).

**Common errors:**
- `401`: Invalid API key - check `SKILL_OPENROUTER_API_KEY`
- `402`: Add credits at openrouter.ai
- `429`: Rate limited - script auto-retries

## Python Usage (Direct Import)

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
