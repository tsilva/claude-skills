---
name: repo-logo-generator
description: Generate logos for GitHub repositories via OpenRouter using two-step workflow (Gemini for quality + GPT-5 for transparency). Works with pixel art, vector designs, and complex multi-colored styles. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
license: MIT
compatibility: python 3.8+, requires requests library, uses OpenRouter skill
metadata:
  version: "3.0.4"
---

# Repo Logo Generator

Generate professional logos with transparent backgrounds using a two-step workflow:
1. **Gemini** (google/gemini-3-pro-image-preview) for superior image quality
2. **GPT-5 Image** (openai/gpt-5-image) for transparent background conversion

This combines the best of both models: Gemini's high-quality generation with GPT-5's transparency capabilities.

## Path Resolution

The two-step generation script must be resolved from the plugin cache using an absolute path. Never use relative paths.

**Dynamic resolution (recommended):**
```bash
# Find latest repo-logo-generator version
LATEST_VERSION=$(ls -1 ~/.claude/plugins/cache/claude-skills/repo-logo-generator 2>/dev/null | sort -V | tail -n 1)
LOGO_SCRIPT="$HOME/.claude/plugins/cache/claude-skills/repo-logo-generator/$LATEST_VERSION/skills/repo-logo-generator/scripts/generate_logo_two_step.py"

# Verify it exists
if [ ! -f "$LOGO_SCRIPT" ]; then
  echo "Error: repo-logo-generator plugin not found. Install via: /skills-discovery repo-logo-generator" >&2
  exit 1
fi

# Use in command
uv run --with requests "$LOGO_SCRIPT" \
  "Your prompt here" \
  --output logo.png
```

**Important:** Always validate that the script exists before attempting to execute it. If not found, inform the user immediately and do not proceed.

## REQUIRED: Execution Checklist (MUST complete in order)

Follow these steps exactly. Do not skip steps or improvise.

- [ ] **Step 0**: Create Todo List
  - Use TodoWrite to create a todo list with these items:
    1. Validate dependencies (find two-step script, check API key)
    2. Load configuration files (project → user → default)
    3. Read project documentation to determine type
    4. Generate logo using two-step workflow (Gemini + GPT-5)
    5. Verify logo file and properties

  This is a multi-step task requiring todo list tracking per TodoWrite guidelines.

- [ ] **Step 1**: Validate Dependencies
  - Locate latest two-step generation script using path resolution logic above
  - Verify `SKILL_OPENROUTER_API_KEY` environment variable is set
  - If either check fails, report to user immediately and do not proceed
  - Mark "Validate dependencies" todo as completed

- [ ] **Step 2**: Load config by reading each path in order (stop at first that exists):
  1. Read `./.claude/readme-generator.json` (project config)
  2. Read `~/.claude/readme-generator.json` (user config)
  3. Read `assets/default-config.json` from this skill's directory (default)

  **IMPORTANT**: Actually READ each file path, don't just search for JSON files.
  Mark "Load configuration files" todo as completed after this step.

- [ ] **Step 3**: Check if config has `style` parameter:
  - **If YES** (user has custom settings): Use the `config.style` value AS-IS for the entire prompt. DO NOT use the template below. DO NOT enforce "no text" or "vector style" rules. The user's style setting completely overrides all defaults.
  - **If NO** (using defaults): Continue to Step 4.

- [ ] **Step 4**: Read project files (README, package.json, etc.) to determine project type
  Mark "Read project documentation" todo as completed after this step.

- [ ] **Step 5**: Select visual metaphor from the table below and fill the prompt template

- [ ] **Step 6**: Generate logo using two-step workflow:
  - Step 6a: Gemini generates high-quality image
  - Step 6b: GPT-5 Image converts to transparent background
  - Both steps are handled by the `generate_logo_two_step.py` script
  - Use absolute path to script (resolved in Step 1)
  - Command format:
    ```bash
    uv run --with requests \
      "$LOGO_SCRIPT" \
      "[YOUR PROMPT HERE]" \
      --output logo.png
    ```
  Mark "Generate logo using two-step workflow" todo as completed after this step.

- [ ] **Step 7**: Verify logo exists and is valid PNG with transparency
  Mark "Verify logo file and properties" todo as completed after this step.

## Sandbox Compatibility

⚠️ **macOS Limitation**: On macOS, `uv run` may require `dangerouslyDisableSandbox: true` because UV accesses system configuration APIs (`SystemConfiguration.framework`) to detect proxy settings. This is a known UV limitation on macOS systems.

**Behavior:**
- On first execution, Claude may attempt with sandbox enabled
- If it fails with system-configuration errors, Claude will retry with sandbox disabled
- This is expected behavior and does not indicate a security issue

**Alternative (for restricted environments):**
If sandbox restrictions are problematic, you can pre-install dependencies:
```bash
python3 -m pip install requests
python3 /absolute/path/to/openrouter_client.py image MODEL "prompt" --output logo.png
```

However, we recommend the standard UV approach for portability and zero-setup benefits.

## Prompt Template (MANDATORY - DO NOT MODIFY FORMAT)

You MUST construct the prompt using this EXACT template. Do not paraphrase, do not add creative flourishes, do not skip any line.

```
A {config.style} logo for {PROJECT_NAME}: {VISUAL_METAPHOR_FROM_TABLE}.
Clean vector style. Icon colors from: {config.iconColors}.
Transparent background. No text, no letters, no words. Single centered icon, geometric shapes, works at {config.size}.
```

**Default values** (when no config exists):
- `config.style` = `minimalist`
- `config.iconColors` = `#ffffff, #58a6ff, #3fb950, #d29922, #a371f7`
- `config.size` = `64x64`
- `config.geminiModel` = `google/gemini-3-pro-image-preview`
- `config.gpt5Model` = `openai/gpt-5-image`

### Filled Example

For a CLI tool called "fastgrep":

```
A minimalist logo for fastgrep: A magnifying glass with speed lines forming a geometric pattern.
Clean vector style. Icon colors from: #ffffff, #58a6ff, #3fb950, #d29922, #a371f7.
Transparent background. No text, no letters, no words. Single centered icon, geometric shapes, works at 64x64.
```

## Visual Metaphors by Project Type (MUST use this table)

Select the metaphor that matches the project type. Do NOT invent alternatives.

| Project Type | Visual Metaphor |
|--------------|-----------------|
| CLI tool | Origami transformation, geometric terminal |
| Library | Interconnected building blocks |
| Web app | Modern interface window, minimal chrome |
| API | Messenger bird carrying data packet |
| Framework | Architectural scaffold, blueprint |
| Tool | Precision instrument, sharp edges |
| Converter | Metamorphosis symbol (butterfly) |
| Runner | Sprinter in motion, speed lines |
| Validator | Wax seal of approval |
| Linter | Elegant brush sweeping |
| Test framework | Test tube with checkmarks |
| Dashboard | Mission control panel |
| Analytics | Magnifying glass revealing patterns |
| Database | Stacked cylinders, data nodes |
| Security | Shield, lock, key |
| Default | Abstract geometric shape |

## ❌ DO NOT

- Invent custom visual metaphors (use the table above)
- Paraphrase the template (use it verbatim with values filled in)
- Add extra descriptive language like "network nodes", "data fragments", "circuit patterns", "flowing streams"
- Skip any line of the template
- Add "gradient", "3D", "glossy", "photorealistic" or similar non-minimalist styles
- Include text, letters, or words in the logo description

## Configuration Reference

Logo generation can be customized via configuration files. Check in order (first found wins):

1. **Project config**: `./.claude/readme-generator.json`
2. **User config**: `~/.claude/readme-generator.json`
3. **Default config**: `assets/default-config.json` (bundled with this skill)

Read JSON if exists, extract `logo` object. Project overrides user overrides default.

### Configurable Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `iconColors` | `["#ffffff", "#58a6ff", "#3fb950", "#d29922", "#a371f7"]` | Preferred icon colors |
| `style` | `minimalist` | Logo style description (completely overrides default prompt if set) |
| `size` | `64x64` | Target size for logo |
| `aspectRatio` | `1:1` | Aspect ratio for generation |
| `geminiModel` | `google/gemini-3-pro-image-preview` | Model for initial high-quality generation (step 1) |
| `gpt5Model` | `openai/gpt-5-image` | Model for transparency conversion (step 2) |

### Example Configuration

**Minimalist style (default):**
```json
{
  "logo": {
    "iconColors": ["#7aa2f7", "#bb9af7", "#7dcfff"],
    "style": "minimalist",
    "geminiModel": "google/gemini-3-pro-image-preview",
    "gpt5Model": "openai/gpt-5-image"
  }
}
```

**Pixel art style (LucasArts adventure game aesthetic):**
```json
{
  "logo": {
    "iconColors": "Vibrant saturated colors inspired by classic LucasArts VGA adventure games",
    "style": "Pixel art in the painterly style of classic LucasArts VGA adventure games (1990s era). Create a charming character mascot with a funny expression. Surround with floating icon-only symbols relevant to the project. Use classic adventure game title banner style with ornate border. Rich dithering, vibrant saturated colors, whimsical and humorous. MUST include the project name as pixel art text in the banner.",
    "geminiModel": "google/gemini-3-pro-image-preview",
    "gpt5Model": "openai/gpt-5-image"
  }
}
```

## Two-Step Workflow: Best of Both Models

**How it works:**
1. **Gemini generates the logo**: Uses `google/gemini-3-pro-image-preview` for superior image quality and design
2. **GPT-5 converts to transparent**: Sends Gemini's output to `openai/gpt-5-image` with "remove background" prompt

This workflow combines:
- Gemini's superior visual design capabilities
- GPT-5 Image's transparency conversion abilities

**Benefits:**
- ✅ **Higher quality** - Gemini produces better designs than GPT-5 alone
- ✅ **Reliable transparency** - GPT-5 successfully converts backgrounds to transparent
- ✅ **No color constraints** - use any colors including magenta/pink
- ✅ **Real alpha channel** - proper RGBA transparency
- ✅ **Works with all styles** - pixel art, vector, complex designs
- ✅ **Clean edges** - AI-generated smooth transparency

**Compatibility:**
- ✅ Multi-colored pixel art (character sprites, detailed scenes)
- ✅ Complex LucasArts/adventure game styles
- ✅ Logos with text labels and detailed shading
- ✅ Minimalist vector designs
- ✅ Any style supported by either model

**Quality:**
The two-step approach consistently produces high-quality logos with proper transparent backgrounds. Testing shows Gemini's superior generation quality combined with GPT-5's reliable transparency conversion.

## Technical Requirements

Logos must meet these criteria:
- **Centered**: Works in circular and square crops
- **High contrast**: Clear visibility on various backgrounds
- **Clean style**: Works at multiple sizes (16x16 to 512x512)
- **Single focal point**: One clear visual element

## Usage

Use the two-step generation script for best quality with transparency:

```bash
# Resolve script path (see Path Resolution section above)
LATEST_VERSION=$(ls -1 ~/.claude/plugins/cache/claude-skills/repo-logo-generator 2>/dev/null | sort -V | tail -n 1)
LOGO_SCRIPT="$HOME/.claude/plugins/cache/claude-skills/repo-logo-generator/$LATEST_VERSION/skills/repo-logo-generator/scripts/generate_logo_two_step.py"

# Generate logo with two-step workflow (Gemini + GPT-5)
uv run --with requests \
  "$LOGO_SCRIPT" \
  "Your logo prompt here" \
  --output logo.png

# Optional: Keep intermediate Gemini image for comparison
uv run --with requests \
  "$LOGO_SCRIPT" \
  "Your logo prompt here" \
  --output logo.png \
  --keep-intermediate
```

**Note on Sandbox Mode**: When Claude runs these commands, it may need to disable sandbox due to `uv` accessing macOS system configuration APIs (see Sandbox Compatibility section above).
