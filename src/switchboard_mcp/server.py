from mcp import ClientSession, StdioServerParameters, stdio_client
from mcp.server.fastmcp import FastMCP

from simple_script.tools import Folder
from switchboard_mcp import utils
from switchboard_mcp.config import MCPServerConfig

mcp = FastMCP("Switchboard MCP Server")


config = MCPServerConfig.from_yaml("switchboard.yaml")


@mcp.tool()
@utils.copy_doc(utils.browse_tools)
async def browse_tools(path: str = "") -> str:
    from simple_script.tools import Tool

    stdio_tools = []
    for server_cfg in config:
        if server_cfg.stdio:
            server_params = StdioServerParameters(
                command=server_cfg.stdio.command,
                args=server_cfg.stdio.args,
                env=server_cfg.stdio.env,
            )
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize
                    await session.initialize()

                    # List and call tools
                    tools_list = await session.list_tools()
                    # Convert MCP tools to custom Tool objects
                    for mcp_tool in tools_list.tools:
                        stdio_tools.append(Tool.from_mcp_tool(mcp_tool))
                        print(f"Tool: {mcp_tool.name}")
        elif server_cfg.sse:
            raise NotImplementedError("SSE transport not implemented yet")

    root = Folder.from_tools(stdio_tools)
    return utils.browse_tools(root, path)


@mcp.tool()
@utils.copy_doc(utils.execute_script)
async def execute_script(script: str) -> str:
    return "cannot run the script, try later"
    # return utils.execute_script(root.tools, script)


if __name__ == "__main__":
    mcp.run(transport="stdio")  # or HTTP etc.
