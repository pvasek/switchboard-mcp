# Switchboard MCP

The idea of this MCP server is to give user a possibility to still include various MCP tools without killing the context.
This is the experimental MCP server which goals is to explore how we could decrease the context size used by MCP hosts.

It tries to cover two things discovery and tool calling:

1. **Discovery** - Most clients list all MCP tools and include all their tools in the context. This means that you can either have a fewer tools enabled or have less context for your instruction/conversation. This MCP give's the possibility to list tools in a hierarchical way. So you don't need to decide which tools you could need neither sacrifice your context for something you probably will not need.

2. **Tool calling** - Right now MCP is designed in a way that the tool is called by MCP host and the data are returned back. The MCP host can use them to call other tool if decides so. This isn't really efficient especially if the data are large. Let's say that the tool want to retrieve data and display them in the graph. This can/is solved by allowing the MCP host the code execution or send-boxed code execution. This on the other hand seems too big. In our experiment we give the MCP host possibility to execute minimal python dsl ([simple script](SIMPLE_SCRIPT.md)). This is the minimum to get MCP host chance to do the basic tool calling and passing parameters around without the full code execution.

## Simple Script

A Python-subset interpreter for tool composition. Supports imports, variables, literals (str/int/list/dict), operators, if/else, while, functions. See [SIMPLE_SCRIPT.md](SIMPLE_SCRIPT.md) for details.

```python
from playwright.navigation import navigate
from playwright.inspection import snapshot
navigate("https://example.com")
page = snapshot()
print(page)
```

## Configuration

Configure MCP servers in `switchboard.yaml`:

```yaml
servers:
  - name: playwright                    # Server name (becomes root namespace)
    stdio:
      command: npx
      args:
        - "@playwright/mcp@latest"
      env:
        PATH: "/usr/local/bin:/usr/bin:/bin"

    # Optional: Strip common prefix from tool names
    remove_prefix: "browser_"

    # Optional: Organize tools into namespaces
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

After organization with `remove_prefix: "browser_"` and namespace mappings:
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
└── test_utils.py       # Tests for namespace mapping, prefix removal

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




