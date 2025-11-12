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
        root = Folder.from_tools(tools)
        return utils.execute_script(root.tools, script)


if __name__ == "__main__":
    mcp.run(transport="stdio")  # or HTTP etc.
