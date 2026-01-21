---
name: settings-cleaner
description: Analyzes and cleans up Claude Code permission whitelists by identifying overly specific approvals, dangerous patterns, and redundant entries. Use when asked to "clean up settings", "review permissions", "optimize allowlist", or "audit security settings". Provides interactive review before making changes.
license: MIT
compatibility: python 3.8+
argument-hint: "[analyze|clean|auto-fix]"
disable-model-invocation: false
user-invocable: true
metadata:
  author: tsilva
  version: "1.0.7"
---

# Settings Cleaner

Audit and optimize Claude Code permission whitelists for security and efficiency.

## Quick Start

**IMPORTANT**: Always run from the user's current working directory and pass the project settings path explicitly.

```bash
# Analyze permissions (read-only)
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with colorama {SKILL_BASE}/scripts/settings_cleaner.py analyze \
  --project-settings {USER_CWD}/.claude/settings.local.json

# Interactive cleanup with confirmation prompts
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with colorama {SKILL_BASE}/scripts/settings_cleaner.py clean \
  --project-settings {USER_CWD}/.claude/settings.local.json

# Auto-fix redundant permissions only (safest, no prompts)
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with colorama {SKILL_BASE}/scripts/settings_cleaner.py auto-fix \
  --project-settings {USER_CWD}/.claude/settings.local.json
```

Where:
- `{SKILL_BASE}` = Absolute path to the skill directory (from Base directory message)
- `{USER_CWD}` = User's current working directory (use `pwd` or equivalent to get absolute path)

**Note on Sandbox Mode**: The `UV_CACHE_DIR=/tmp/claude/uv-cache` prefix ensures `uv` uses an allowed cache directory. When Claude runs these commands, it may still need to disable sandbox due to `uv` accessing macOS system configuration APIs. Users running commands manually won't encounter this restriction.

## What It Checks

The skill categorizes permissions into four types:

### 🔴 Dangerous Patterns

Overly broad permissions that grant unrestricted access:
- `Bash(*:*)` - Any bash command
- `Read(/*)` - Read any file on system
- `Write(/*)` - Write any file on system
- `Edit(/*)` - Edit any file on system
- `Bash(rm:*)` - Any rm command
- `Bash(sudo:*)` - Any sudo command
- `Skill(*)` - Any skill without restriction

### 🟡 Overly Specific Patterns

Exact commands with hardcoded arguments that should be generalized:
- `Bash(python test.py --verbose)` → Suggest `Bash(python:*)`
- `Bash(npm install express)` → Suggest `Bash(npm:*)`
- `Bash(git commit -m "message")` → Suggest `Bash(git:*)`

### 🔵 Redundant Permissions

Project permissions already covered by broader global permissions:
- Global has `Bash(python:*)`, project has `Bash(python test.py)` → Redundant
- Global has `WebFetch`, project has `WebFetch(domain:example.com)` → Redundant
- Global has `Bash(*:*)`, project has any `Bash(...)` → Redundant

### ✅ Good Permissions

Well-scoped permissions that follow best practices:
- `Bash(pytest:*)` - All pytest commands
- `Read(/Users/tsilva/repos/*)` - Scoped to specific directory
- `WebFetch(domain:api.openrouter.ai)` - Specific domain

### 🔍 Self-Awareness

When you run this tool, it checks if it's analyzing its own permissions:
- `Skill(settings-cleaner)` - Specific permission for this tool
- `Skill(*)` - Wildcard access to all skills (flagged as DANGEROUS)

The tool will note when it detects itself and provide guidance on whether the permission should be retained.

## Commands

| Command | Description | Modifications |
|---------|-------------|---------------|
| `analyze` | Read-only audit of permissions | None (report only) |
| `clean` | Interactive cleanup with confirmations | Yes (with prompts) |
| `auto-fix` | Remove redundant permissions automatically | Yes (redundancies only) |

## Example Output

```
=== Claude Code Settings Analysis ===

📋 CONTEXT:
  Global settings: /Users/username/.claude/settings.json
  Project settings: /Users/username/project/.claude/settings.local.json

  🔍 Self-awareness detected:
    - Skill(settings-cleaner) [Project]
    Note: This analysis tool is whitelisted in your permissions.
    Recommendation: Review if this permission should persist after cleanup.

🔴 DANGEROUS (1 found):
  - Bash(*:*) [Global]
    Risk: Allows unrestricted access

🟡 OVERLY SPECIFIC (2 found):
  - Bash(python test.py --verbose) [Project]
    → Suggest: Bash(python:*)

🔵 REDUNDANT (1 found):
  - Bash(pytest:*) [Project]
    Covered by: Bash(python:*) [Global]

✅ GOOD (5 permissions)

Total issues: 4
```

## Safety Features

1. **Automatic backups**: Creates `.bak` files before any modifications
2. **Interactive mode**: Prompts for each dangerous/specific pattern
3. **Auto-fix safety**: Only removes redundancies (no dangerous/specific changes)
4. **JSON validation**: Verifies structure after loading and before saving
5. **Color-coded output**: Clear visual categorization of issues

## Implementation Notes

### Pattern Matching

The skill uses pattern subsetting logic to determine redundancy:

```python
# Tool-level wildcards
WebFetch covers WebFetch(domain:*)

# Command-level wildcards
Bash(python:*) covers Bash(python ...) with any arguments
Bash(*:*) covers all Bash commands

# Exact matches
Bash(ls -la) only covers that exact command
```

### Files Analyzed

- **Global**: `~/.claude/settings.json`
- **Project**: `./.claude/settings.local.json`

Only the `permissions.allow[]` array is reviewed.

## Usage from Claude Code

Trigger the skill by asking:
- "Clean up my settings"
- "Review my permissions"
- "Audit my security settings"
- "Optimize my allowlist"
- "Check for redundant permissions"

### Execution Instructions for Claude

When this skill is invoked, you MUST follow this workflow:

1. **Get the skill base directory** from the "Base directory for this skill" message
2. **Get the user's current working directory** (they're already in the right place)
3. **Read the settings files FIRST** (before running the script):
   - Read global settings: `~/.claude/settings.json`
   - Read project settings (if exists): `{USER_CWD}/.claude/settings.local.json`

   **Why read first?**
   - Provides context for the analysis
   - Allows you to give preliminary assessment
   - Helps catch file existence issues early
   - Enables better recommendations

4. **Run the analysis script** with absolute paths:
   ```bash
   UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with colorama {SKILL_BASE}/scripts/settings_cleaner.py analyze \
     --project-settings {USER_CWD}/.claude/settings.local.json
   ```

5. **Show the findings** to the user (script provides formatted output)
6. **Ask if they want to proceed** with cleanup
7. **Execute cleanup command** if requested (clean or auto-fix mode)

**Important**: The script needs to find the project's `.claude/settings.local.json` file in the user's working directory, not in the skill's directory. Always use absolute paths.
