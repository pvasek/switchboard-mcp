from mcp.server.fastmcp import FastMCP

from simple_script.tools import Folder
from switchboard_mcp import utils
from switchboard_mcp.config import MCPServerConfig
from switchboard_mcp.session_manager import SessionManager

mcp = FastMCP("Switchboard MCP Server")


config = MCPServerConfig.from_yaml("switchboard.yaml")


@mcp.tool()
@utils.copy_doc(utils.browse_tools)
async def browse_tools(path: str = "") -> str:
    async with SessionManager(config) as manager:
        tools = await manager.get_all_tools()
        root = Folder.from_tools(tools)
        return utils.browse_tools(root, path)


@mcp.tool()
@utils.copy_doc(utils.execute_script)
async def execute_script(script: str) -> str:
    async with SessionManager(config) as manager:
        tools = await manager.get_all_tools()
        return await utils.execute_script(tools, script)


if __name__ == "__main__":
    import sys

    # Parse command-line arguments for transport selection
    transport = "stdio"  # Default to stdio for compatibility

    if len(sys.argv) > 1:
        transport = sys.argv[1].lower()
        # Map "http" to "streamable-http" (FastMCP's actual transport name)
        if transport == "http":
            transport = "streamable-http"
        if transport not in ["stdio", "streamable-http"]:
            print(f"Invalid transport: {transport}. Valid options: stdio, http")
            print("Using stdio instead.")
            transport = "stdio"

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        # For streamable-http, host/port are configured in FastMCP constructor
        # Default is 127.0.0.1:8000
        print("Starting MCP server on HTTP at http://127.0.0.1:8000")
        mcp.run(transport=transport)
