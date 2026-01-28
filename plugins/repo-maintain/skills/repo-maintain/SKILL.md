---
name: repo-maintain
description: Audits and remediates repos in current directory for standardization. Use when maintaining repos, checking README/logo/gitignore compliance, or syncing GitHub descriptions.
argument-hint: "[audit|fix|status] [repo-filter]"
license: MIT
metadata:
  author: tsilva
  version: "1.4.2"
---

# Repo Maintain

Audit and remediate repositories for standardization compliance.

## Prerequisites

Before any operation, verify dependencies:

**Required Skills:**
- `project-readme-author` - README creation/optimization
- `project-logo-author` - logo generation

**Required Tools:**
- `git` - repo detection
- `gh` CLI - GitHub API operations
- `mcp__image-tools__get_image_metadata` - logo transparency check

If any are missing, inform user with specific installation steps.

## Operations

| Operation | Triggers | Purpose |
|-----------|----------|---------|
| `audit` | "audit", "check", "scan", no args + no report | Run all checks, output JSON |
| `fix` | "fix", "remediate", "repair" | Work through audit findings |
| `status` | "status", "progress", no args + report exists | Show summary and progress |

### Operation Detection

Use the deterministic operation selector for consistent behavior:

```bash
uv run shared/select_operation.py --skill repo-maintain --args "$ARGUMENTS" --check-files ""
```

The script returns JSON with the selected operation and reasoning:
```json
{"operation": "audit", "reason": "No explicit operation keyword", "source": "file_state"}
```

**Fallback rules (if script unavailable):**
1. Check `$ARGUMENTS` for explicit operation keyword
2. If no keyword: check for existing report at `~/.claude/repo-maintain-audit.json`
   - Report exists → `status`
   - No report → `audit`

## Audit Workflow

1. Run the audit script:
   ```bash
   uv run scripts/audit.py --repos-dir "$(pwd)"
   ```

2. Report saved to `~/.claude/repo-maintain-audit.json`

3. Display summary showing:
   - Total repos found
   - Pass rate percentage
   - Failed checks grouped by repo

### Audit Checks (per-repo)

| Check | Detection | Auto-Fix |
|-------|-----------|----------|
| README_EXISTS | File exists | `project-readme-author create` |
| README_CURRENT | Staleness heuristics | `project-readme-author optimize` |
| README_HAS_LICENSE | License section in README | Append `## License` section |
| LOGO_EXISTS | Standard locations | `project-logo-author` |
| LOGO_HAS_NAME | Read image visually | Regenerate logo |
| LOGO_TRANSPARENT | `mcp__image-tools__get_image_metadata` | Regenerate logo |
| LICENSE_EXISTS | LICENSE/LICENSE.md/LICENSE.txt | Copy MIT from `assets/LICENSE` |
| GITIGNORE_EXISTS | File exists | Create from template |
| GITIGNORE_COMPLETE | Pattern check | Append missing entries |
| CLAUDE_MD_EXISTS | File exists | `/init` |
| CLAUDE_SETTINGS_SANDBOX | .claude/settings*.json or sandbox in CLAUDE.md | Create settings.local.json |
| DEPENDABOT_EXISTS | .github/dependabot.yml exists | Create from template |
| DESCRIPTION_SYNCED | gh API vs README tagline | `gh repo edit --description` |
| PII_CLEAN | Regex patterns | Manual review |
| PYTHON_PYPROJECT | File exists if Python | Generate pyproject.toml |
| PYTHON_UV_INSTALL | `uv sync --dry-run` | Fix pyproject.toml |

## Fix Workflow

### Step 1: Apply Safe Fixes Automatically

Before manual intervention, run the safe fix applier to handle trivial fixes:

```bash
uv run scripts/apply_safe_fixes.py --audit-report ~/.claude/repo-maintain-audit.json
```

**Safe fixes (auto-applied):**
- `GITIGNORE_EXISTS` - Copy template gitignore
- `LICENSE_EXISTS` - Copy MIT license with year/author
- `CLAUDE_MD_EXISTS` - Create minimal CLAUDE.md
- `CLAUDE_SETTINGS_SANDBOX` - Create/update settings.json with sandbox enabled
- `DEPENDABOT_EXISTS` - Create dependabot.yml with detected ecosystems

**Unsafe fixes (returned for Claude):**
- `README_EXISTS` - Requires content generation
- `LOGO_EXISTS` - Requires image generation
- `README_CURRENT` - Requires content analysis
- `DESCRIPTION_SYNCED` - Requires API calls
- `PII_CLEAN` - Requires manual review

The script returns JSON showing what was applied and what remains:
```json
{
  "applied": [{"repo": "my-project", "check": "LICENSE_EXISTS", "message": "Created LICENSE"}],
  "remaining": [{"repo": "my-project", "check": "README_EXISTS", "auto_fix": "project-readme-author create"}],
  "summary": {"applied_count": 3, "remaining_count": 5}
}
```

### Step 2: Process Remaining Fixes

Process repos in order. For each repo with remaining failures:

### Fix Order (dependencies matter)

1. **CLAUDE.md** - Run `/init` in repo directory
2. **Claude Settings** - Create `.claude/settings.local.json` with sandbox enabled:
   ```json
   {
     "sandbox": {
       "enabled": true
     },
     "permissions": {
       "allow": [],
       "deny": []
     }
   }
   ```
   Or bulk fix: `uv run scripts/fix_sandbox.py --repos-dir "$(pwd)"`
3. **LICENSE** - Copy from `assets/LICENSE`, replace `[year]` with current year, `[fullname]` with GitHub user
4. **Logo** - Invoke `project-logo-author`
5. **Logo checks** (if logo exists):
   - Read logo with Read tool
   - Check transparency: `mcp__image-tools__get_image_metadata`
   - If logo has text/name or not transparent → regenerate
6. **README** - Invoke `project-readme-author create` or `optimize`
7. **README License** - Append `## License\n\nMIT` if missing
8. **.gitignore**:
   - If missing: create from `assets/gitignore-template.txt`
   - If incomplete: append missing patterns
9. **Dependabot** - Create `.github/dependabot.yml`:
   - Auto-detects relevant ecosystems (npm, pip, cargo, gomod, etc.)
   - Always includes github-actions for workflow updates
   - Sets weekly update schedule
10. **Description sync**:
    - Use `scripts/extract_tagline.py` for robust tagline extraction
    - Run: `gh repo edit --description "tagline"`
    - Or bulk sync: `uv run scripts/sync_descriptions.py --repos-dir "$(pwd)"`
11. **Python fixes**:
    - Generate pyproject.toml if missing
    - Fix errors shown by uv
12. **PII alerts** - List findings for manual review (don't auto-fix)

### Progress Tracking

Track progress in `~/.claude/repo-maintain-progress.json`:

```json
{
  "audit_file": "~/.claude/repo-maintain-audit.json",
  "started_at": "ISO timestamp",
  "last_repo": "repo-name",
  "completed": ["repo-a", "repo-b"],
  "skipped": {"repo-c": "reason"},
  "remaining": ["repo-d"]
}
```

After each repo:
1. Update progress file
2. Report what was fixed
3. Move to next repo

If interrupted, resume from `last_repo`.

## Status Workflow

1. Read audit report from `~/.claude/repo-maintain-audit.json`
2. Read progress from `~/.claude/repo-maintain-progress.json` (if exists)
3. Display:
   - Audit summary (repos, pass rate)
   - Remediation progress (completed/remaining)
   - Current failures by check type

## Dependabot Template

Template at `assets/dependabot.yml` creates automated dependency update PRs.

**Auto-detected ecosystems:**
- `github-actions` - Always included if `.github/workflows/` exists
- `npm` - If `package.json` exists
- `pip` - If `pyproject.toml` or `requirements.txt` exists
- `cargo` - If `Cargo.toml` exists
- `gomod` - If `go.mod` exists
- `bundler` - If `Gemfile` exists
- `composer` - If `composer.json` exists

All ecosystems use weekly update schedule.

## Gitignore Template

Template at `assets/gitignore-template.txt` contains:
- Credential patterns (.env, *.pem, *.key)
- Build artifacts (__pycache__, node_modules, dist)
- OS files (.DS_Store)
- IDE files (.idea, .vscode)
- Claude Code files (.claude-sandbox.json)

## Tagline Extraction

The `scripts/extract_tagline.py` extracts README taglines for GitHub description sync:

```bash
uv run scripts/extract_tagline.py /path/to/README.md
```

Handles complex README structures:
- YAML frontmatter (`---` blocks)
- Centered divs with logos, titles, badges
- Bold formatting (`**tagline**` → `tagline`)
- Badge lines (`[![`, `![`)
- Link-only lines
- Emoji preservation
- GitHub 350 char limit

## Bulk Description Sync

The `scripts/sync_descriptions.py` syncs descriptions for multiple repos:

```bash
# Preview changes (dry run)
uv run scripts/sync_descriptions.py --repos-dir /path/to/repos --dry-run

# Apply changes
uv run scripts/sync_descriptions.py --repos-dir /path/to/repos

# Filter by repo name
uv run scripts/sync_descriptions.py --repos-dir /path/to/repos --filter "my-project"

# JSON output
uv run scripts/sync_descriptions.py --repos-dir /path/to/repos --json
```

## PII Scanner

The `scripts/pii_scanner.py` detects:
- AWS keys (AKIA pattern)
- GitHub tokens (gh[ps]_ pattern)
- Private keys (BEGIN PRIVATE KEY)
- Database URLs with credentials
- Generic passwords/secrets

Respects .gitignore - only scans tracked files.

## Usage Examples

```
/repo-maintain audit              # Audit all repos in CWD
/repo-maintain audit my-project   # Audit repos matching "my-project"
/repo-maintain fix                # Fix all issues (in order)
/repo-maintain fix my-project     # Fix specific repo
/repo-maintain status             # Show progress
```
