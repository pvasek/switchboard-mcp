import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Coroutine, List, TypeVar

import mcp
from mcp import ClientSession, StdioServerParameters, stdio_client

from simple_script.tools import Tool
from switchboard_mcp.config import MCPServerConfig

T = TypeVar("T")


def run_async_in_loop(
    co_routine: Coroutine[Any, Any, T],
    loop: asyncio.AbstractEventLoop,
    timeout: float = 120,
) -> T:
    """Run a coroutine in a specific event loop from a synchronous context.

    This schedules the coroutine on the given loop and waits for the result.
    The loop must be running in another thread.
    """
    future = asyncio.run_coroutine_threadsafe(co_routine, loop)
    try:
        return future.result(timeout=timeout)
    except TimeoutError:
        future.cancel()
        raise asyncio.TimeoutError(f"Coroutine timed out after {timeout} seconds")


def create_mcp_adapter(
    session: ClientSession, tool: mcp.Tool, loop: asyncio.AbstractEventLoop
) -> Callable[..., Any]:
    # Extract parameter names in order from the tool's schema
    param_names = []
    if hasattr(tool, "inputSchema") and tool.inputSchema:
        properties = tool.inputSchema.get("properties", {})
        param_names = list(properties.keys())

    def tool_adapter(*args: Any, **kwargs: Any) -> Any:
        # Map positional arguments to parameter names
        params = dict(zip(param_names, args))
        # Merge with keyword arguments (kwargs take precedence)
        params.update(kwargs)
        return run_async_in_loop(session.call_tool(tool.name, params), loop)

    return tool_adapter


@dataclass
class SessionHolder:
    session: ClientSession
    session_cm: Any  # ClientSession context manager
    stdio_cm: Any  # stdio_client context manager


class SessionManager:
    def __init__(self, server_configs: List[MCPServerConfig]):
        self.server_configs = server_configs
        self.sessions: List[SessionHolder] = []  # Store SessionHolder instances
        self.loop: asyncio.AbstractEventLoop | None = None

    async def __aenter__(self):
        """Open all sessions"""
        # Store the event loop for sync->async bridging
        self.loop = asyncio.get_running_loop()

        for server_cfg in self.server_configs:
            if server_cfg.stdio:
                server_params = StdioServerParameters(
                    command=server_cfg.stdio.command,
                    args=server_cfg.stdio.args,
                    env=server_cfg.stdio.env,
                )
                # Create and store the stdio context manager
                stdio_cm = stdio_client(server_params)
                read, write = await stdio_cm.__aenter__()

                # Create and store the session context manager
                session_cm = ClientSession(read, write)
                session = await session_cm.__aenter__()

                # Initialize the session
                await session.initialize()

                # Store all components for cleanup
                self.sessions.append(SessionHolder(session, session_cm, stdio_cm))

            elif server_cfg.sse:
                raise NotImplementedError("SSE transport not implemented yet")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close all sessions, guaranteed to run even on exception"""
        # Close in reverse order
        for session_holder in reversed(self.sessions):
            try:
                # Close session first
                await session_holder.session_cm.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                print(f"Error closing session: {e}")

            try:
                # Close stdio connection
                await session_holder.stdio_cm.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                print(f"Error closing stdio: {e}")

        self.sessions.clear()
        return False  # Don't suppress exceptions

    async def get_all_tools(self) -> List[Tool]:
        """Get all tools from all active sessions"""
        if self.loop is None:
            raise RuntimeError(
                "SessionManager must be entered as context manager first"
            )

        all_tools = []

        for session_holder in self.sessions:
            tools_list = await session_holder.session.list_tools()
            for mcp_tool in tools_list.tools:
                all_tools.append(
                    Tool.from_mcp_tool(
                        mcp_tool,
                        create_mcp_adapter(session_holder.session, mcp_tool, self.loop),
                    )
                )

        return all_tools
