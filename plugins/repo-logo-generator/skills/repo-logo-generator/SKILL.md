---
name: repo-logo-generator
description: Generates logos for GitHub repositories using mcp-openrouter with programmatic transparency conversion. Works with pixel art, vector designs, and complex multi-colored styles. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
license: MIT
compatibility: requires mcp-openrouter and mcp-image-tools MCP servers
argument-hint: "[style-preference]"
disable-model-invocation: false
user-invocable: true
metadata:
  version: "4.5.0"
---

# Repo Logo Generator

Generate professional logos with transparent backgrounds using:
1. **mcp-openrouter** - generates logo with solid chromakey background
2. **mcp-image-tools** - converts background to transparent with smooth edges

## Execution Workflow

Follow these steps exactly.

### Step 1: Load Configuration

Read config files in order (merge: project > user > bundled):
1. `./.claude/repo-logo-generator.json` (project config)
2. `~/.claude/repo-logo-generator.json` (user config)
3. `assets/default-config.json` (bundled defaults)

**Config Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `promptTemplate` | null | Full prompt template (null = use default) |
| `style` | `"minimalist"` | Style descriptor |
| `visualMetaphor` | null | Override metaphor, `"none"` to omit |
| `includeRepoName` | `false` | Include project name as stylized text |
| `iconColors` | `["#58a6ff", ...]` | Design colors |
| `additionalInstructions` | `""` | Appended to prompt |
| `keyColor` | `"#00FF00"` | Chromakey background |
| `tolerance` | `70` | Chromakey edge tolerance |
| `model` | `"google/gemini-3-pro-image-preview"` | Image model |
| `size` | `"1K"` | Image size |
| `outputPath` | `"logo.png"` | Output file path |
| `compress` | `true` | Enable PNG compression |
| `compressQuality` | `80` | Compression quality |

### Step 2: Gather Context (Always Runs)

Gather these values for template variable substitution:

| Variable | Source |
|----------|--------|
| `{PROJECT_NAME}` | Current directory name |
| `{PROJECT_TYPE}` | Auto-detected from package files |
| `{VISUAL_METAPHOR}` | config.visualMetaphor OR auto-select from table |
| `{STYLE}` | config.style |
| `{ICON_COLORS}` | config.iconColors joined with ", " |
| `{KEY_COLOR}` | config.keyColor |
| `{TEXT_INSTRUCTIONS}` | If `includeRepoName`: `Include "{PROJECT_NAME}" as stylized text.` else `No text, no letters, no words.` |

**Visual Metaphors by Project Type:**

| Type | Metaphor |
|------|----------|
| CLI tool | Origami transformation, geometric terminal |
| Library | Interconnected building blocks |
| Web app | Modern interface window |
| API | Messenger bird carrying data packet |
| Framework | Architectural scaffold |
| Converter | Metamorphosis symbol |
| Database | Stacked cylinders, data nodes |
| Security | Shield, lock, key |
| Default | Abstract geometric shape |

Set `visualMetaphor: "none"` in config to omit the metaphor entirely.

### Step 3: Build Prompt

**If `config.promptTemplate` is set:** Use it as the prompt template.

**Otherwise, use default template:**
```
A {STYLE} logo for {PROJECT_NAME}: {VISUAL_METAPHOR}.
Clean vector style. Icon colors from: {ICON_COLORS}.
Pure {KEY_COLOR} background only. Do not use similar tones in the design.
{TEXT_INSTRUCTIONS} Single centered icon, geometric shapes, works at 64x64.
```

**Then:**
1. Substitute ALL template variables in the prompt
2. Append `config.additionalInstructions` if non-empty

### Step 4: Generate Image

Use `mcp__openrouter__generate_image`:
- `model`: config.model
- `prompt`: constructed prompt from Step 3
- `output_path`: `/tmp/claude/logo_raw.png`
- `aspect_ratio`: `"1:1"`
- `size`: config.size

### Step 5: Apply Chromakey Transparency

Use `mcp__image-tools__chromakey_to_transparent`:
- `input_path`: `/tmp/claude/logo_raw.png`
- `output_path`: config.outputPath (with variable substitution)
- `key_color`: config.keyColor
- `tolerance`: config.tolerance

### Step 6: Compress (if enabled)

If `config.compress` is true, use `mcp__image-tools__compress_png`:
- `input_path`: config.outputPath
- `quality`: config.compressQuality

### Step 7: Verify Output

Confirm the output file exists and is a valid PNG with transparency.

## Configuration Examples

**Default behavior (no config needed):**
```json
{}
```

**Use project name in custom style:**
```json
{
  "logo": {
    "style": "SNES pixel art for {PROJECT_NAME}. Charming mascot. Pure {KEY_COLOR} background."
  }
}
```

**Full custom prompt:**
```json
{
  "logo": {
    "promptTemplate": "A {STYLE} icon for {PROJECT_NAME}. Colors: {ICON_COLORS}. Solid {KEY_COLOR} bg."
  }
}
```

**Magenta chromakey (for green-heavy designs):**
```json
{
  "logo": {
    "keyColor": "#FF00FF",
    "style": "nature-themed with greens and blues"
  }
}
```

**Pixel art with custom output path:**
```json
{
  "logo": {
    "style": "16-bit pixel art. Visible chunky pixels with dithering. Bright saturated colors. Pure {KEY_COLOR} background.",
    "outputPath": "assets/{PROJECT_NAME}-logo.png"
  }
}
```

**Include project name as text:**
```json
{
  "logo": {
    "includeRepoName": true,
    "style": "SNES pixel art with banner"
  }
}
```

## Guidelines

- Avoid green tones in icons when using default `#00FF00` keyColor (reserved for chromakey)
- Avoid magenta tones when using `#FF00FF` keyColor
- When `includeRepoName: false` (default), logos have no text for small-size clarity
- Always complete the chromakey step for transparency
