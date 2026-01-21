---
name: repo-logo-generator
description: Generate logos for GitHub repositories via OpenRouter using Gemini with programmatic transparency conversion. Works with pixel art, vector designs, and complex multi-colored styles. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
license: MIT
compatibility: python 3.8+, requires requests and pillow libraries, uses OpenRouter skill
argument-hint: "[style-preference]"
disable-model-invocation: false
user-invocable: true
metadata:
  version: "3.2.0"
---

# Repo Logo Generator

Generate professional logos with transparent backgrounds using chromakey technology:
1. **Gemini** (google/gemini-3-pro-image-preview) generates logo with green (#00FF00) background
2. **PIL** applies professional chromakey algorithm for smooth transparency

The chromakey approach eliminates "halo" artifacts around edges that occur with white background conversion. This is the same technique used in film/TV green screen compositing (hence "green screen").

## Path Resolution

The logo generation script must be resolved from the plugin cache using an absolute path. Never use relative paths.

**Dynamic resolution (recommended):**
```bash
# Find latest repo-logo-generator version
LATEST_VERSION=$(ls -1 ~/.claude/plugins/cache/claude-skills/repo-logo-generator 2>/dev/null | sort -V | tail -n 1)
LOGO_SCRIPT="$HOME/.claude/plugins/cache/claude-skills/repo-logo-generator/$LATEST_VERSION/skills/repo-logo-generator/scripts/generate_logo.py"

# Verify it exists
if [ ! -f "$LOGO_SCRIPT" ]; then
  echo "Error: repo-logo-generator plugin not found. Install via: /skills-discovery repo-logo-generator" >&2
  exit 1
fi

# Use in command
uv run --with requests --with pillow "$LOGO_SCRIPT" \
  "Your prompt here" \
  --output logo.png
```

**Important:** Always validate that the script exists before attempting to execute it. If not found, inform the user immediately and do not proceed.

## REQUIRED: Execution Checklist (MUST complete in order)

Follow these steps exactly. Do not skip steps or improvise.

- [ ] **Step 0**: Create Todo List
  - Use TodoWrite to create a todo list with these items:
    1. Validate dependencies (find script, check API key)
    2. Load configuration files (project → user → default)
    3. Read project documentation to determine type
    4. Generate logo using Gemini with chromakey background
    5. Verify logo file and properties

  This is a multi-step task requiring todo list tracking per TodoWrite guidelines.

- [ ] **Step 1**: Validate Dependencies
  - Locate latest generation script using path resolution logic above
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

  **CRITICAL: Chromakey Color Handling**
  - The `--key-color` flag MUST use `config.keyColor` (default: `#00FF00` green)
  - NEVER infer `--key-color` from background colors mentioned in the `style` text
  - The style text tells Gemini what to generate; `keyColor` tells PIL what color to remove
  - If the style mentions "white background", "magenta background", etc., IGNORE it for `--key-color`
  - Only use a non-green `--key-color` if `config.keyColor` is explicitly set in the JSON

- [ ] **Step 4**: Read project files (README, package.json, etc.) to determine project type
  Mark "Read project documentation" todo as completed after this step.

- [ ] **Step 5**: Select visual metaphor from the table below and fill the prompt template

- [ ] **Step 6**: Generate logo:
  - Gemini generates image with green (#00FF00) chromakey background
  - PIL applies chromakey algorithm for smooth transparent edges
  - Use absolute path to script (resolved in Step 1)
  - Command format:
    ```bash
    uv run --with requests --with pillow \
      "$LOGO_SCRIPT" \
      "[YOUR PROMPT HERE]" \
      --output logo.png
    ```
  Mark "Generate logo" todo as completed after this step.

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
python3 -m pip install requests pillow
python3 /absolute/path/to/generate_logo.py "prompt" --output logo.png
```

However, we recommend the standard UV approach for portability and zero-setup benefits.

## Prompt Template (MANDATORY - DO NOT MODIFY FORMAT)

You MUST construct the prompt using this EXACT template. Do not paraphrase, do not add creative flourishes, do not skip any line.

```
A {config.style} logo for {PROJECT_NAME}: {VISUAL_METAPHOR_FROM_TABLE}.
Clean vector style. Icon colors from: {config.iconColors}.
Pure bright green (#00FF00) background only. Do not use green tones anywhere in the design.
No text, no letters, no words. Single centered icon, geometric shapes, works at {config.size}.
```

**Default values** (when no config exists):
- `config.style` = `minimalist`
- `config.iconColors` = `#58a6ff, #d29922, #a371f7, #7aa2f7, #f97583` (avoid green)
- `config.size` = `64x64`
- `config.model` = `google/gemini-3-pro-image-preview`
- `config.keyColor` = `#00FF00` (green)
- `config.tolerance` = `70`

### Filled Example

For a CLI tool called "fastgrep":

```
A minimalist logo for fastgrep: A magnifying glass with speed lines forming a geometric pattern.
Clean vector style. Icon colors from: #58a6ff, #d29922, #a371f7, #7aa2f7, #f97583.
Pure bright green (#00FF00) background only. Do not use green tones anywhere in the design.
No text, no letters, no words. Single centered icon, geometric shapes, works at 64x64.
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
- Use green tones in the icon colors - green is reserved for the chromakey background
- Infer `--key-color` from background colors in the style text (ALWAYS use `config.keyColor` or default green)

## Configuration Reference

Logo generation can be customized via configuration files. Check in order (first found wins):

1. **Project config**: `./.claude/readme-generator.json`
2. **User config**: `~/.claude/readme-generator.json`
3. **Default config**: `assets/default-config.json` (bundled with this skill)

Read JSON if exists, extract `logo` object. Project overrides user overrides default.

### Configurable Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `iconColors` | `["#58a6ff", "#d29922", "#a371f7", "#7aa2f7", "#f97583"]` | Preferred icon colors (avoid green) |
| `style` | `minimalist` | Logo style description (completely overrides default prompt if set) |
| `size` | `64x64` | Target size for logo |
| `aspectRatio` | `1:1` | Aspect ratio for generation |
| `model` | `google/gemini-3-pro-image-preview` | Model for image generation |
| `keyColor` | `#00FF00` | Chromakey background color (green recommended) |
| `tolerance` | `70` | Chromakey tolerance for transparency (0-255, higher = more aggressive) |

### Example Configuration

**Minimalist style (default):**
```json
{
  "logo": {
    "iconColors": ["#7aa2f7", "#bb9af7", "#7dcfff"],
    "style": "minimalist",
    "model": "google/gemini-3-pro-image-preview",
    "keyColor": "#00FF00",
    "tolerance": 70
  }
}
```

**Pixel art style (SNES/LucasArts aesthetic):**
```json
{
  "logo": {
    "iconColors": "SVGA high-color palette with maximum saturation and vibrancy. Vivid reds, bright oranges, golden yellows, electric cyans, deep blues, bold purples. Avoid green tones.",
    "style": "SNES 16-bit pixel art (Chrono Trigger style). Charming character mascot representing the project concept. VISIBLE CHUNKY PIXELS with dithering for shading. Selective outlines. Full SNES color palette, bright and saturated. Floating icon-only symbols (no text on icons). Banner with project name as pixel art text. Pure bright green (#00FF00) background only - do not use green anywhere else in the design.",
    "keyColor": "#00FF00",
    "tolerance": 70,
    "model": "google/gemini-3-pro-image-preview"
  }
}
```

## How It Works: Chromakey Transparency

**Professional-quality workflow:**
1. **Gemini generates the logo**: Uses `google/gemini-3-pro-image-preview` with green (#00FF00) background
2. **PIL applies chromakey**: Professional algorithm calculates proportional alpha for smooth edges

This is the same technique used in film/TV green screen compositing, adapted for logo generation.

**Why Green (Not Magenta or White)?**

- **White background** has a fundamental problem: anti-aliased edges blend toward white, creating "halo" artifacts
- **Magenta background** conflicts with purple/violet tones common in pixel art and colorful designs (LucasArts, SNES aesthetics)
- **Green background** is industry standard because green is rarely used in character art, logos, and icons

Chromakey solves edge artifacts:
- **Distinct hue detection**: Green has a specific hue (120°), easily distinguished from most design colors
- **Proportional alpha**: Blended pixels get partial transparency, creating smooth edges
- **Preserves all colors**: Purple, magenta, pink, and light colors in designs are unaffected

**Benefits:**
- ✅ **Smooth edges** - No halo artifacts around anti-aliased pixels
- ✅ **Professional quality** - Industry-standard compositing technique
- ✅ **Works with purple/magenta designs** - Common in pixel art and colorful styles
- ✅ **Single API call** - Fast and cost-effective
- ✅ **Deterministic** - Consistent, reproducible results

**Compatibility:**
- ✅ Multi-colored designs (just avoid green in the icon)
- ✅ Pixel art, vector, and complex styles
- ✅ Logos with or without text
- ✅ Minimalist or detailed designs
- ✅ Purple/magenta designs (LucasArts, SNES aesthetics)

**Alternative Key Colors:**
If your design requires green tones, you can use magenta chromakey instead:
```bash
uv run --with requests --with pillow "$LOGO_SCRIPT" "prompt" --output logo.png --key-color "#FF00FF"
```

**Legacy Mode:**
If you need the old white background approach, use the `--white-bg` flag:
```bash
uv run --with requests --with pillow "$LOGO_SCRIPT" "prompt" --output logo.png --white-bg
```

## Technical Requirements

Logos must meet these criteria:
- **Centered**: Works in circular and square crops
- **High contrast**: Clear visibility on various backgrounds
- **Clean style**: Works at multiple sizes (16x16 to 512x512)
- **Single focal point**: One clear visual element

## Usage

Use the generation script with Gemini + chromakey for transparent logos:

```bash
# Resolve script path (see Path Resolution section above)
LATEST_VERSION=$(ls -1 ~/.claude/plugins/cache/claude-skills/repo-logo-generator 2>/dev/null | sort -V | tail -n 1)
LOGO_SCRIPT="$HOME/.claude/plugins/cache/claude-skills/repo-logo-generator/$LATEST_VERSION/skills/repo-logo-generator/scripts/generate_logo.py"

# Generate logo with chromakey transparency (default)
uv run --with requests --with pillow \
  "$LOGO_SCRIPT" \
  "Your logo prompt here" \
  --output logo.png

# Keep original image before transparency conversion
uv run --with requests --with pillow \
  "$LOGO_SCRIPT" \
  "Your logo prompt here" \
  --output logo.png \
  --keep-original

# Adjust chromakey tolerance (default 70, higher = more aggressive)
uv run --with requests --with pillow \
  "$LOGO_SCRIPT" \
  "Your logo prompt here" \
  --output logo.png \
  --tolerance 80

# Use custom key color (default: green #00FF00)
# Use magenta if your design needs green tones
uv run --with requests --with pillow \
  "$LOGO_SCRIPT" \
  "Your logo prompt here" \
  --output logo.png \
  --key-color "#FF00FF"

# Legacy mode: Use white background instead of chromakey
uv run --with requests --with pillow \
  "$LOGO_SCRIPT" \
  "Your logo prompt here" \
  --output logo.png \
  --white-bg
```

**Note on Sandbox Mode**: When Claude runs these commands, it may need to disable sandbox due to `uv` accessing macOS system configuration APIs (see Sandbox Compatibility section above).
