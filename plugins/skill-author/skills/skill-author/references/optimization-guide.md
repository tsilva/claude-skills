# Skill Optimization Guide

Comprehensive guide for improving skill instruction following, token efficiency, and trigger accuracy.

## Description Engineering

The description is Claude's primary signal for skill selection. A well-crafted description dramatically improves trigger accuracy.

### Keyword Strategy

Include words users naturally say when they need your skill:

| Domain | Keywords to Include |
|--------|---------------------|
| File Processing | "extract", "convert", "parse", "generate" |
| Code Quality | "review", "lint", "validate", "check" |
| Documentation | "document", "README", "explain", "describe" |
| Deployment | "deploy", "build", "release", "publish" |

### Trigger Phrase Patterns

Explicit triggers help Claude match user intent:

```yaml
# Pattern 1: "Use when" clause
description: Generate API documentation. Use when asked to document APIs or create OpenAPI specs.

# Pattern 2: Domain keywords
description: Process PDF files - extract text, fill forms, merge documents. Triggers on PDF operations.

# Pattern 3: Action enumeration
description: Commit, push, create PRs, manage branches. Use for git workflow tasks.
```

### Description Anti-Patterns

| Bad | Problem | Better |
|-----|---------|--------|
| "Helps with code" | Too vague, no triggers | "Review code for bugs and security issues. Use when reviewing PRs." |
| "A tool for projects" | No action verbs | "Initialize project structure. Use when starting new projects." |
| "Does various things" | No specificity | "Generate, validate, and format JSON schemas." |

## Instruction Architecture

Use the WIRE framework for clear, unambiguous instructions.

### W - Workflow (Steps)

Number your steps explicitly. Claude follows numbered sequences reliably:

```markdown
## Workflow

1. Read the input file
2. Parse the configuration
3. Generate output based on template
4. Write to destination path
```

**Avoid narrative flow:**
```markdown
# Bad - narrative style
First you should read the file, then you can parse it. After that,
generate the output and finally write it.
```

### I - Inputs (Parameters)

Define inputs with types and constraints:

```markdown
## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| file_path | string | yes | Absolute path to input file |
| format | enum | no | Output format: json, yaml, toml (default: json) |
| verbose | bool | no | Show detailed output (default: false) |
```

### R - Rules (Constraints)

State constraints as explicit rules, not suggestions:

```markdown
## Rules

- ALWAYS use absolute paths
- NEVER modify files outside the working directory
- Output format MUST match the specified type
```

### E - Examples (Concrete)

One good example beats three mediocre ones:

```markdown
## Example

Input: `/path/to/config.yaml`
Output: `/path/to/config.json`

The skill reads the YAML, converts to JSON with 2-space indentation.
```

## Token Efficiency Patterns

### Decision Tree: What Goes Where

```
Is this needed for EVERY invocation?
├─ Yes → Keep in SKILL.md body
└─ No
   ├─ Needed for MOST invocations? → Keep in SKILL.md, compress it
   └─ Needed only sometimes?
      ├─ Is it a decision/algorithm? → Move to scripts/
      └─ Is it reference material? → Move to references/
```

### Scripts vs Inline Code

**Use scripts when:**
- Logic is deterministic and repeatable
- Code exceeds 20 lines
- Multiple steps with error handling
- Needs testing/validation

**Keep inline when:**
- Simple one-liners or examples
- Configuration snippets
- Explaining concepts (not executing)

### Progressive Disclosure

Structure information in tiers:

1. **Always loaded** (SKILL.md body): Core workflow, primary rules
2. **Loaded on demand** (references/): Deep dives, edge cases, examples
3. **Executed on demand** (scripts/): Deterministic operations

### Compression Techniques

| Technique | Before | After | Savings |
|-----------|--------|-------|---------|
| Remove filler words | "You should always make sure to" | "Always" | ~80% |
| Tables over prose | 5-line explanation | 2-row table | ~60% |
| Code over description | "Create a file with X content" | Actual code block | ~40% |
| Reference extraction | 500-char section | "See references/detail.md" | ~95% |

## Anti-Patterns Deep Dive

### 1. Explaining Obvious Operations

**Problem:** Telling Claude what it already knows.

```markdown
# Bad
When reading a file, use the Read tool. The Read tool takes a file path
and returns the contents. Make sure the path exists before reading.

# Good
Read the configuration file.
```

Claude knows how to read files. Only specify when behavior differs from default.

### 2. Multiple Equivalent Examples

**Problem:** Several examples showing the same concept.

```markdown
# Bad - three examples of the same thing
Example 1: Generate README for Python project
Example 2: Generate README for JavaScript project
Example 3: Generate README for Go project

# Good - one canonical example with note
Example: Generate README for Python project

Works for any language - auto-detects from project structure.
```

### 3. Verbose Error Handling Instructions

**Problem:** Detailed error handling that Claude handles naturally.

```markdown
# Bad
If the file doesn't exist, show an error message to the user explaining
that the file was not found and suggest they check the path.

# Good
# (omit entirely - Claude handles missing files appropriately)
```

### 4. Hardcoded Paths

**Problem:** Paths that break across environments.

```markdown
# Bad
Read /Users/john/projects/config.json

# Good
Read the config.json file in the project root.
```

### 5. Missing Workflow Order

**Problem:** Ambiguous execution sequence.

```markdown
# Bad
The skill validates input, generates output, and logs results.

# Good
1. Validate input against schema
2. Generate output from template
3. Log results to console
```

## Before/After Examples

### Description Optimization

**Before (62 chars, vague):**
```yaml
description: A helpful tool for working with documentation files.
```

**After (142 chars, specific triggers):**
```yaml
description: Generate and update README files with badges, installation, and usage sections. Use when creating docs or asked about documentation.
```

### Instruction Clarity

**Before (narrative, ambiguous):**
```markdown
This skill helps you process data files. You can use it to read CSV
files and convert them. It supports various output formats. Make sure
to specify what format you want.
```

**After (structured, clear):**
```markdown
## Workflow

1. Read input CSV file
2. Convert to specified format
3. Write output file

## Supported Formats

| Format | Extension |
|--------|-----------|
| JSON | .json |
| YAML | .yaml |
| XML | .xml |
```

### Token Efficiency

**Before (inline, 400+ chars):**
```markdown
When validating, check that the name field exists and is between 1-64
characters, contains only lowercase letters numbers and hyphens, doesn't
start or end with hyphen, doesn't have consecutive hyphens, matches the
directory name, and doesn't contain "anthropic"...
```

**After (script reference, 50 chars):**
```markdown
Run validation:
```bash
python scripts/validate.py $PATH
```
```

## Testing Checklist

### Pre-Release Validation

- [ ] Run `validate_skill.py` with zero errors
- [ ] Description under 1024 chars
- [ ] Description includes trigger phrases
- [ ] SKILL.md body under 500 lines
- [ ] Character budget under 15,000
- [ ] All paths are relative or auto-detected
- [ ] Workflow steps are numbered
- [ ] No obvious operation explanations

### Trigger Testing

Test these phrases with your skill:

1. Direct invocation: `/skill-name`
2. Keyword match: "Can you [keyword from description]?"
3. Domain match: "[domain term] this file"
4. Negative test: Unrelated request should NOT trigger

### Model Testing Matrix

| Test | Expected |
|------|----------|
| Explicit invocation | Always triggers |
| Keyword in description | Usually triggers |
| Similar domain task | May trigger (acceptable) |
| Unrelated task | Never triggers |

## Quick Reference

### Optimal Description Formula

```
[Action verb] + [domain objects] + ". Use when " + [trigger phrases] + "."
```

Example:
```yaml
description: Validate API schemas and generate TypeScript types. Use when reviewing API designs or creating type definitions.
```

### SKILL.md Size Targets

| Component | Target | Max |
|-----------|--------|-----|
| Description | 100-200 chars | 1024 chars |
| Body | 200-400 lines | 500 lines |
| Total | 8,000-12,000 chars | 15,000 chars |

### Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| ERROR | Blocks functionality | Must fix |
| WARNING | May cause issues | Should fix |
| SUGGESTION | Could improve | Consider |
