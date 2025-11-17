import asyncio
import sys

from fastmcp import FastMCP

from switchboard_mcp import utils
from switchboard_mcp.config import MCPServerConfig
from switchboard_mcp.session_manager import SessionManager
from switchboard_mcp.utils import Folder

config = MCPServerConfig.from_yaml("switchboard.yaml")
mcp = FastMCP("Switchboard MCP Server")


async def setup_tools():
    # Startup
    async with SessionManager(config) as manager:
        tool_groups = await manager.get_all_tools()

        def browse_tools(path: str) -> str:
            root = Folder.from_tools(tool_groups)
            return utils.browse_tools(root, path)

        browse_tools_docs = f"""Browse tools organized in a hierarchical structure using dot notation.
Shows subnamespaces and functions with their parameters and descriptions.    

Args:
    path: Dot-separated path (e.g., "math.statistics")
        Empty string or no argument lists root level

Returns:
    String with subnamespaces listed first, then functions with parameters and descriptions

{browse_tools("")}
"""

        async def execute_script(script: str) -> str:
            async with SessionManager(config) as manager:
                tool_groups = await manager.get_all_tools()
                # Flatten tool groups to get all tools for script execution
                all_tools = []
                for group in tool_groups:
                    all_tools.extend(group.tools)
                return await utils.execute_script(all_tools, script)

        mcp.tool(
            browse_tools,
            name="browse_tools",
            description=browse_tools_docs,
        )
        mcp.tool(
            execute_script,
            name="execute_script",
            description=utils.execute_script.__doc__,
        )


if __name__ == "__main__":
    asyncio.run(setup_tools())
    # Parse command-line arguments for transport selection
    transport = "stdio"  # Default to stdio for compatibility

    if len(sys.argv) > 1:
        transport = sys.argv[1].lower()
        if transport not in ["stdio", "http"]:
            print(f"Invalid transport: {transport}. Valid options: stdio, http")
            print("Using stdio instead.")
            transport = "stdio"

    if transport == "stdio":
        mcp.run(transport=transport)
    else:
        # For streamable-http, host/port are configured in FastMCP constructor
        # Default is 127.0.0.1:8000
        print("Starting MCP server on HTTP at http://127.0.0.1:8000")
        mcp.run(transport=transport)
