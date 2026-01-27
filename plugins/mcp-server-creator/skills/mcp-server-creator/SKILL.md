---
name: mcp-server-creator
description: Creates MCP servers using FastMCP with production-ready patterns. Use when asked to "create an MCP server", "build MCP tools", or integrate external APIs with Claude Code.
license: MIT
compatibility: python 3.10+, requires uv
argument-hint: "[server-name]"
user-invocable: true
metadata:
  author: tsilva
  version: "1.0.1"
---

# MCP Server Creator

Create production-ready MCP servers for Claude Code integration.

## Project Structure

```
mcp-{name}/
├── src/mcp_{name}/
│   ├── __init__.py      # Package exports
│   ├── __main__.py      # Entry point
│   ├── server.py        # MCP tool definitions
│   ├── client.py        # API client (if complex)
│   └── config.py        # Environment configuration
├── tests/
│   └── test_tools.py    # Tool tests
├── pyproject.toml       # Package config
├── .env.example         # Environment template
├── .gitignore
├── CLAUDE.md            # Claude instructions
└── README.md
```

## Execution Checklist

1. **Gather requirements** - API name, base URL, authentication method
2. **Create directory structure** - `mkdir -p mcp-{name}/src/mcp_{name} mcp-{name}/tests`
3. **Copy templates** - Read from `assets/templates/`, substitute variables
4. **Create initial tools** - Based on API capabilities
5. **Add installation instructions** to CLAUDE.md
6. **Test with** `uv sync && uv run mcp-{name}`

## Variable Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `{SERVER_NAME}` | Hyphenated name | `mcp-weather` |
| `{PACKAGE_NAME}` | Python package | `mcp_weather` |
| `{API_NAME}` | Human readable | `Weather API` |
| `{API_KEY_VAR}` | Env variable | `WEATHER_API_KEY` |
| `{API_BASE_URL}` | Base endpoint | `https://api.weather.com/v1` |
| `{CLIENT_CLASS}` | Class name | `WeatherClient` |
| `{AUTHOR}` | GitHub username | `tsilva` |

## Architecture Patterns

### Server-Only (Simple APIs)

For 1-3 endpoints, put all logic in `server.py`:

```python
@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    response = httpx.get(f"{BASE_URL}/weather", params={"q": city})
    response.raise_for_status()
    return json.dumps(response.json(), indent=2)
```

### Server + Client (Production APIs)

Separate concerns when:
- Multiple endpoints share authentication
- Rate limiting or retry logic needed
- Response processing is complex

`server.py` handles MCP interface, `client.py` handles API logic.

## Error Handling

### Classification

| Status | Type | Action |
|--------|------|--------|
| 400 | Non-retryable | User-friendly error message |
| 401 | Non-retryable | "Invalid API key" |
| 402 | Non-retryable | "API quota exceeded" |
| 403 | Non-retryable | "Permission denied" |
| 408, 429 | Retryable | Exponential backoff |
| 502, 503 | Retryable | Exponential backoff |

### Pattern

```python
class APIError(Exception):
    def __init__(self, message: str, status_code: int = None, retryable: bool = False):
        self.status_code = status_code
        self.retryable = retryable
        super().__init__(message)

def handle_response(response: httpx.Response) -> dict:
    if response.status_code == 401:
        raise APIError("Invalid API key. Check {API_KEY_VAR}.", 401)
    if response.status_code == 429:
        raise APIError("Rate limited. Try again later.", 429, retryable=True)
    response.raise_for_status()
    return response.json()
```

## Tool Registration

### Basic Tool

```python
@mcp.tool()
def tool_name(required_param: str, optional_param: str = "default") -> str:
    """Tool description becomes Claude's understanding of what this does.

    Args:
        required_param: What this parameter controls
        optional_param: Optional configuration
    """
    client = get_client()
    return client.do_something(required_param)
```

### Tool with Complex Types

```python
from typing import Optional, Literal

@mcp.tool()
def search(
    query: str,
    limit: int = 10,
    sort: Literal["relevance", "date"] = "relevance"
) -> str:
    """Search with filters."""
    # Implementation
```

## Configuration Pattern

### Package-Relative .env Loading

```python
from pathlib import Path
from dotenv import load_dotenv

_package_dir = Path(__file__).parent.parent.parent
load_dotenv(_package_dir / ".env")

API_KEY = os.getenv("{API_KEY_VAR}")
if not API_KEY:
    raise ValueError("{API_KEY_VAR} environment variable required")
```

## Installation

### Claude Code

```bash
claude mcp add {name} --scope user -- uv run --directory /absolute/path/to/mcp-{name} mcp-{name}
```

### VS Code (settings.json)

```json
{
  "mcpServers": {
    "{name}": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-{name}", "mcp-{name}"]
    }
  }
}
```

### Environment Variables

Add to `~/.claude/.env` or project `.env`:
```
{API_KEY_VAR}=your_api_key_here
```

## Testing

### Quick Validation

```bash
cd mcp-{name}
uv sync
uv run mcp-{name}  # Should start without errors
```

### Tool Testing

```bash
uv run pytest tests/ -v
```

## Template Files

All templates are in `assets/templates/`. Read each file and substitute variables.

| Template | Purpose |
|----------|---------|
| `pyproject.toml.template` | Package configuration |
| `server.py.template` | MCP server with example tools |
| `client.py.template` | API client class |
| `config.py.template` | Environment loading |
| `__init__.py.template` | Package exports |
| `__main__.py.template` | Entry point |
| `CLAUDE.md.template` | Claude instructions |
| `.env.example.template` | Environment template |
| `.gitignore.template` | Git ignores |
| `test_tools.py.template` | Basic tests |

## Workflow Summary

1. Ask user for: server name, API name, base URL, auth method
2. Derive variables: `{PACKAGE_NAME}` = name with underscores, `{CLIENT_CLASS}` = PascalCase
3. Create directory structure
4. Read each template, substitute variables, write to target
5. Add 2-3 initial tools based on API documentation
6. Test server starts: `uv run mcp-{name}`
7. Provide installation command
