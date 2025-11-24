# Switchboard MCP

An aggregator MCP server that connects multiple MCP servers into a unified interface while minimizing context usage. Think of it as a switchboard operator routing between different services.

**The Problem**: MCP clients typically load all tool definitions into context upfront. With 5+ MCP servers providing 100+ tools, you quickly hit context limits, forcing you to choose between having many tools available or having room for actual conversation.

**The Experiment**: This project tests two strategies to reduce context consumption:

## 1. Hierarchical Discovery

Instead of loading all tools at once, organize them in modules and load definitions on-demand:

```
❌ Flat (loads 100 tool definitions immediately):
playwright_browser_navigate, playwright_browser_click, playwright_browser_snapshot, ...

✅ Hierarchical (loads structure first, details when browsing):
playwright/
  ├─ navigation/     (4 tools)
  ├─ interaction/    (5 tools)
  └─ inspection/     (4 tools)
```

Browse `playwright.navigation` → only then load those 4 tool definitions into context.

## 2. Minimal Script Execution

Enable basic tool composition without full code execution. Instead of:
1. MCP Host → Tool A → returns large dataset → MCP Host
2. MCP Host processes data → Tool B → MCP Host
3. MCP Host → Tool C with transformed data

Run a simple script:
```python
# Using selective imports
from api import fetch_data, transform
from graph import plot
data = fetch_data("endpoint")
result = transform(data)
plot(result)

# Or using module aliases
import api.data as data_api
import graph.visualize as viz
dataset = data_api.fetch("endpoint")
viz.plot(dataset)
```

The data stays server-side, only final output returns to the host. Uses a minimal Python-like DSL ([simple script](SIMPLE_SCRIPT.md)) - not full Python execution.

## Simple Script

A Python-subset interpreter for tool composition. Supports two import styles (selective and aliased), variables, literals (str/int/list/dict), operators, if/else, while, functions. See [SIMPLE_SCRIPT.md](SIMPLE_SCRIPT.md) for details.

```python
# Selective imports
from playwright.navigation import navigate
from playwright.inspection import snapshot

# Module aliases
import playwright.interaction as interact

navigate("https://example.com")
interact.click("button[type='submit']")
page = snapshot()
print(page)
```

## Configuration

Configure MCP servers in `switchboard.yaml`:

```yaml
servers:
  - name: playwright                    # Server name (becomes root module)
    stdio:
      command: npx
      args:
        - "@playwright/mcp@latest"
      env:
        PATH: "/usr/local/bin:/usr/bin:/bin"

    # Optional: Strip common prefix from tool names
    remove_prefix: "browser_"

    # Optional: Organize tools into modules
    namespace_mappings:
      - namespace: "navigation"         # Creates playwright.navigation
        tools:
          - "browser_navigate*"         # Pattern: prefix match
          - "browser_navigate_back"     # Exact match
          - "browser_close"
          - "browser_install"

      - namespace: "interaction"        # Creates playwright.interaction
        tools:
          - "browser_click"
          - "browser_hover"
          - "browser_type"
```

### Tool Transformation

Original tools from playwright MCP:
```
browser_navigate, browser_click, browser_hover, ...
```

After organization with `remove_prefix: "browser_"` and module mappings:
```
playwright.navigation.navigate()      # browser_navigate → navigate
playwright.navigation.close()         # browser_close → close
playwright.interaction.click()        # browser_click → click
playwright.interaction.hover()        # browser_hover → hover
```

## Development

### Project Structure

```
src/switchboard_mcp/
├── config.py           # YAML config loading, server definitions
├── session_manager.py  # MCP client session management
├── utils.py            # Tool organization, browsing, script execution
└── server.py           # FastMCP server with browse_tools/execute_script

test/
└── test_utils.py       # Tests for module mapping, prefix removal

switchboard.yaml        # Server configuration
```

### Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest -v
```




