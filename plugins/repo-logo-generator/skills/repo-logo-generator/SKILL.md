---
name: repo-logo-generator
description: Generate logos for GitHub repositories via OpenRouter using Gemini with programmatic transparency conversion. Works with pixel art, vector designs, and complex multi-colored styles. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
license: MIT
compatibility: python 3.8+, requires requests and pillow libraries, uses OpenRouter skill
argument-hint: "[style-preference]"
disable-model-invocation: false
user-invocable: true
metadata:
  version: "3.0.7"
---

# Repo Logo Generator

Generate professional logos with transparent backgrounds using a simplified workflow:
1. **Gemini** (google/gemini-3-pro-image-preview) generates logo with #ffffff background
2. **PIL** programmatically converts #ffffff pixels to transparent

This approach is simpler, faster, and requires only one API call.

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
    4. Generate logo using Gemini with #ffffff background
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

- [ ] **Step 4**: Read project files (README, package.json, etc.) to determine project type
  Mark "Read project documentation" todo as completed after this step.

- [ ] **Step 5**: Select visual metaphor from the table below and fill the prompt template

- [ ] **Step 6**: Generate logo:
  - Gemini generates image with #ffffff background
  - PIL programmatically converts #ffffff to transparent
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
Pure white (#ffffff) background only. Do not use white (#ffffff) anywhere else in the design.
No text, no letters, no words. Single centered icon, geometric shapes, works at {config.size}.
```

**Default values** (when no config exists):
- `config.style` = `minimalist`
- `config.iconColors` = `#58a6ff, #3fb950, #d29922, #a371f7, #7aa2f7` (no white)
- `config.size` = `64x64`
- `config.model` = `google/gemini-3-pro-image-preview`

### Filled Example

For a CLI tool called "fastgrep":

```
A minimalist logo for fastgrep: A magnifying glass with speed lines forming a geometric pattern.
Clean vector style. Icon colors from: #58a6ff, #3fb950, #d29922, #a371f7, #7aa2f7.
Pure white (#ffffff) background only. Do not use white (#ffffff) anywhere else in the design.
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
- Use white (#ffffff) in the icon colors - white is reserved for the background only

## Configuration Reference

Logo generation can be customized via configuration files. Check in order (first found wins):

1. **Project config**: `./.claude/readme-generator.json`
2. **User config**: `~/.claude/readme-generator.json`
3. **Default config**: `assets/default-config.json` (bundled with this skill)

Read JSON if exists, extract `logo` object. Project overrides user overrides default.

### Configurable Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `iconColors` | `["#58a6ff", "#3fb950", "#d29922", "#a371f7", "#7aa2f7"]` | Preferred icon colors (do not include white) |
| `style` | `minimalist` | Logo style description (completely overrides default prompt if set) |
| `size` | `64x64` | Target size for logo |
| `aspectRatio` | `1:1` | Aspect ratio for generation |
| `model` | `google/gemini-3-pro-image-preview` | Model for image generation |
| `tolerance` | `10` | White pixel tolerance for transparency conversion (0-255) |

### Example Configuration

**Minimalist style (default):**
```json
{
  "logo": {
    "iconColors": ["#7aa2f7", "#bb9af7", "#7dcfff"],
    "style": "minimalist",
    "model": "google/gemini-3-pro-image-preview",
    "tolerance": 10
  }
}
```

**Pixel art style (LucasArts adventure game aesthetic):**
```json
{
  "logo": {
    "iconColors": "Vibrant saturated colors inspired by classic LucasArts VGA adventure games (but not white)",
    "style": "Pixel art in the painterly style of classic LucasArts VGA adventure games (1990s era). Create a charming character mascot with a funny expression. Surround with floating icon-only symbols relevant to the project. Use classic adventure game title banner style with ornate border. Rich dithering, vibrant saturated colors, whimsical and humorous. MUST include the project name as pixel art text in the banner.",
    "model": "google/gemini-3-pro-image-preview"
  }
}
```

## How It Works: Gemini + Programmatic Transparency

**Simple, efficient workflow:**
1. **Gemini generates the logo**: Uses `google/gemini-3-pro-image-preview` with #ffffff background
2. **PIL converts to transparent**: Programmatically replaces all #ffffff pixels with transparency

This approach is simpler, faster, and more reliable than multi-step AI conversions.

**Benefits:**
- ✅ **High quality** - Gemini produces excellent designs
- ✅ **Reliable transparency** - Deterministic color replacement, no AI guesswork
- ✅ **No color constraints** - Use any colors except white in the icon
- ✅ **Perfect alpha channel** - Clean RGBA transparency
- ✅ **Faster** - Single API call instead of two
- ✅ **Lower cost** - Half the API usage
- ✅ **Consistent results** - No variation in transparency conversion

**Compatibility:**
- ✅ Multi-colored designs (just avoid white in the icon)
- ✅ Pixel art, vector, and complex styles
- ✅ Logos with or without text
- ✅ Minimalist or detailed designs
- ✅ Any style that works without white in the foreground

**Quality:**
This approach produces high-quality logos with perfect transparent backgrounds. The programmatic conversion is more reliable than AI-based transparency removal.

## Technical Requirements

Logos must meet these criteria:
- **Centered**: Works in circular and square crops
- **High contrast**: Clear visibility on various backgrounds
- **Clean style**: Works at multiple sizes (16x16 to 512x512)
- **Single focal point**: One clear visual element

## Usage

Use the generation script with Gemini + PIL for transparent logos:

```bash
# Resolve script path (see Path Resolution section above)
LATEST_VERSION=$(ls -1 ~/.claude/plugins/cache/claude-skills/repo-logo-generator 2>/dev/null | sort -V | tail -n 1)
LOGO_SCRIPT="$HOME/.claude/plugins/cache/claude-skills/repo-logo-generator/$LATEST_VERSION/skills/repo-logo-generator/scripts/generate_logo.py"

# Generate logo with transparent background
uv run --with requests --with pillow \
  "$LOGO_SCRIPT" \
  "Your logo prompt here" \
  --output logo.png

# Optional: Keep original image with white background for comparison
uv run --with requests --with pillow \
  "$LOGO_SCRIPT" \
  "Your logo prompt here" \
  --output logo.png \
  --keep-original

# Optional: Adjust white pixel tolerance (default 10)
uv run --with requests --with pillow \
  "$LOGO_SCRIPT" \
  "Your logo prompt here" \
  --output logo.png \
  --tolerance 5
```

**Note on Sandbox Mode**: When Claude runs these commands, it may need to disable sandbox due to `uv` accessing macOS system configuration APIs (see Sandbox Compatibility section above).
