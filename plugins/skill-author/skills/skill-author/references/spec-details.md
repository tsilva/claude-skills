# SKILL.md Specification Details

Full reference for the [Agent Skills Specification](https://agentskills.io/specification).

## Table of Contents

- [Frontmatter Fields](#frontmatter-fields)
  - [Required Fields](#required-fields)
  - [Optional Fields](#optional-fields)
- [Progressive Disclosure Tiers](#progressive-disclosure-tiers)
- [Size Limits Summary](#size-limits-summary)
- [Validation Rules Summary](#validation-rules-summary)
- [File Structure](#file-structure)
- [Internal Validation Hooks](#internal-validation-hooks)

## Frontmatter Fields

### Required Fields

#### `name`

- **Type:** string
- **Constraints:**
  - 1-64 characters
  - Lowercase letters (a-z), numbers (0-9), hyphens (-) only
  - No leading or trailing hyphens
  - No consecutive hyphens (--)
  - Must exactly match parent directory name
  - Cannot contain "anthropic" (reserved, ERROR)
  - Cannot use "claude-" prefix (ERROR)
  - Cannot contain XML characters (`<`, `>`)
  - Should avoid vague terms: "helper", "utils", "tools", "documents", "data", "files", "misc", "common", "general" (warning)
- **Purpose:** Becomes the slash command (`/name`)
- **Best Practice:** Prefer gerund-form naming (e.g., "processing-pdfs" vs "pdf-processor")

#### `description`

- **Type:** string
- **Constraints:**
  - 1-1024 characters
  - Non-empty (cannot be whitespace only)
  - Cannot contain XML characters (`<`, `>`) - use plain text
- **Best Practices:**
  - Write in third person ("Generates..." not "Generate...")
  - Include trigger phrases ("Use when...", "Triggers on...")
  - Include keywords Claude can match against
  - Describe both WHAT and WHEN
  - Avoid time-sensitive language ("currently", "as of version X")

### Optional Fields

#### `license`

- **Type:** string
- **Constraints:** None
- **Repository Rule:** Use `MIT` for all skills in this repo

#### `compatibility`

- **Type:** string
- **Constraints:** Max 500 characters
- **Purpose:** Environment requirements
- **Examples:**
  - `python 3.8+`
  - `requires mcp-openrouter MCP server`
  - `macOS and Linux only`

#### `metadata`

- **Type:** key-value mapping (object)
- **Purpose:** Author, version, custom properties
- **Standard Keys:**
  - `author`: Your name/handle
  - `version`: Semantic version (e.g., "1.0.0")
- **Example:**
  ```yaml
  metadata:
    author: your-name
    version: "1.0.0"
    category: utility
  ```

#### `allowed-tools`

- **Type:** space-delimited string
- **Purpose:** Pre-approved tools (experimental)
- **Example:** `Read Glob Grep Bash(npm*)`

#### `argument-hint`

- **Type:** string
- **Purpose:** Shows in autocomplete what arguments the slash command expects
- **Examples:**
  - `[file-path]`
  - `[issue-number]`
  - `[analyze|clean|auto-fix]`
  - `[project|plugin] [skill-name]`

#### `disable-model-invocation`

- **Type:** boolean
- **Default:** `false`
- **Purpose:** When `true`, skill can only be invoked manually via `/name`
- **Use Case:** Prevent accidental triggering for destructive operations

#### `user-invocable`

- **Type:** boolean
- **Default:** `true`
- **Purpose:** When `false`, hides skill from `/` menu
- **Note:** Claude can still trigger it automatically based on description

## Progressive Disclosure Tiers

Skills use 3-tier loading to minimize context usage:

### Tier 1: Metadata (~100 tokens)

- Loaded at startup for ALL installed skills
- Contains: `name` and `description` only
- Used for: Skill selection, matching user intent

### Tier 2: SKILL.md Body (<5000 tokens)

- Loaded when skill triggers (explicit `/name` or auto-triggered)
- Contains: Everything between `---` markers and end of file
- Budget: **15,000 characters maximum** (hard limit)

### Tier 3: Bundled Resources (variable)

- Loaded on-demand when Claude reads them
- Located in:
  - `scripts/` - Executable code
  - `references/` - Additional documentation
  - `assets/` - Static files (templates, icons)
- Keep references one level deep from SKILL.md

## Size Limits Summary

| Element | Limit | Enforcement |
|---------|-------|-------------|
| `name` | 64 chars | Error |
| `description` | 1024 chars | Error |
| `compatibility` | 500 chars | Error |
| SKILL.md total | 15,000 chars | Error |
| Body lines | 500 lines | Warning |

## Validation Rules Summary

### Errors (Must Fix)

| Rule | Field | Description |
|------|-------|-------------|
| Required fields | name, description | Both are mandatory |
| Name format | name | Lowercase, hyphens, 1-64 chars |
| Directory match | name | Must match parent directory name |
| Reserved "anthropic" | name | Cannot contain "anthropic" |
| No XML in name | name | Cannot contain `<` or `>` |
| No XML in description | description | Cannot contain `<` or `>` |
| Character budget | SKILL.md | Max 15,000 characters |
| Version sync | version | Must match across SKILL.md, plugin.json, marketplace.json |

### Warnings (Should Fix)

| Rule | Field | Description |
|------|-------|-------------|
| Body length | body | Warning if >500 lines |
| Windows paths | body | Use forward slashes `/` not backslashes `\` |
| Vague names | name | Avoid "helper", "utils", "tools", etc. |
| Missing files | body | Referenced markdown links should exist |

### Suggestions (--suggest flag)

| Rule | Field | Description |
|------|-------|-------------|
| Gerund naming | name | Prefer "processing-pdfs" over "pdf-processor" |
| Trigger phrases | description | Include "Use when..." for better activation |
| Third-person | description | Start with verbs like "Generates..." |
| Time-sensitive | body | Avoid "currently", "as of version X" |
| TOC for references | references/ | Files >100 lines should have table of contents |
| MCP qualified names | body | Use `mcp__server__tool` format |
| Nested references | references/ | Avoid references linking to other references |

## File Structure

```
skill-name/
├── SKILL.md          # Required - skill definition and instructions
├── scripts/          # Executable code Claude can run
│   └── *.py          # Python scripts (use UV for deps)
├── references/       # On-demand documentation
│   └── *.md          # Detailed guides, specs
└── assets/           # Static resources
    └── *             # Templates, icons, fonts
```

- **scripts/**: Token-efficient - code runs without loading into context
- **references/**: Loaded only when Claude needs detailed information
- **assets/**: Output files, never loaded into context

## Internal Validation Hooks

Skills can provide optional internal validation via `scripts/validate_hook.py`. This allows skills to define their own validation logic that runs automatically when `validate_skill.py` is executed.

### Protocol

The hook receives:
- First argument: absolute path to skill directory
- Optional `--suggest` flag for optimization hints

Must output JSON to stdout:
```json
{
  "issues": [
    {
      "severity": "ERROR|WARNING|SUGGESTION",
      "file_path": "relative/path/to/file",
      "field": "field_name",
      "message": "Description of the issue"
    }
  ]
}
```

Exit codes:
- `0` = hook ran successfully (issues may exist in JSON output)
- Non-zero = hook execution failed

### Error Handling

| Scenario | Behavior |
|----------|----------|
| Hook not found | Skip silently |
| Hook returns valid JSON with issues | Merge into main validation result |
| Hook returns non-zero exit | Report as ERROR |
| Hook returns invalid JSON | Report as ERROR |
| Hook times out (30s) | Report as WARNING, continue |

### Use Cases

- Validate bundled config schemas (e.g., default-config.json)
- Cross-reference SKILL.md documentation with actual files
- Check internal consistency between multiple config files
- Verify required assets exist
