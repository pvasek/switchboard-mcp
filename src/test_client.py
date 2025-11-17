#!/usr/bin/env python3
"""Interactive MCP test client for switchboard_mcp server.

This client can connect to the switchboard MCP server in different modes:
- stdio: Spawn a new server process and connect via stdin/stdout (default)
- http: Connect to an existing HTTP server via streamable-http transport

Usage:
    python src/test_client.py                               # Connect via stdio (new instance)
    python src/test_client.py --transport http              # Connect to HTTP server at 127.0.0.1:8000
    python src/test_client.py --transport http --host 127.0.0.1 --port 8000  # Custom host/port

To debug both server and client together:
    1. Start server: python -m switchboard_mcp.server http
    2. Start client: python src/test_client.py --transport http
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

try:
    import readline
except ImportError:
    readline = None  # type: ignore

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client


class MCPTestClient:
    """Interactive MCP test client."""

    # History file location in user's home directory
    HISTORY_FILE = Path.home() / ".mcp_test_client_history"

    def __init__(
        self,
        transport: str = "stdio",
        host: str = "127.0.0.1",
        port: int = 8000,
    ):
        self.transport = transport
        self.host = host
        self.port = port
        self.session: ClientSession | None = None
        self.stdio_context = None
        self.http_context = None
        self.session_context = None
        self.last_script: str = ""

        # Load last script from disk
        self._load_last_script()

    def _load_last_script(self) -> None:
        """Load the last executed script from disk."""
        try:
            if self.HISTORY_FILE.exists():
                self.last_script = self.HISTORY_FILE.read_text(encoding="utf-8")
        except Exception:
            # Silently ignore errors - history is optional
            pass

    def _save_last_script(self) -> None:
        """Save the last executed script to disk."""
        try:
            self.HISTORY_FILE.write_text(self.last_script, encoding="utf-8")
        except Exception:
            # Silently ignore errors - history is optional
            pass

    async def connect(self) -> None:
        """Connect to the MCP server."""
        print(f"Connecting to MCP server via {self.transport}...")

        if self.transport == "stdio":
            # Spawn new server process and connect via stdio
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "switchboard_mcp.server"],
                env=None,
            )
            self.stdio_context = stdio_client(server_params)
            read, write = await self.stdio_context.__aenter__()

            self.session_context = ClientSession(read, write)
            self.session = await self.session_context.__aenter__()

        elif self.transport == "http":
            # Connect to existing HTTP server using streamable-http transport
            url = f"http://{self.host}:{self.port}/mcp"
            self.http_context = streamablehttp_client(url)
            read, write, _get_session_id = await self.http_context.__aenter__()

            self.session_context = ClientSession(read, write)
            self.session = await self.session_context.__aenter__()
        else:
            raise ValueError(f"Unknown transport: {self.transport}")

        # Initialize the session
        await self.session.initialize()
        print("Connected successfully!\n")

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self.session_context:
            await self.session_context.__aexit__(None, None, None)
        if self.stdio_context:
            await self.stdio_context.__aexit__(None, None, None)
        if self.http_context:
            await self.http_context.__aexit__(None, None, None)
        print("\nDisconnected from server.")

    async def list_tools(self) -> None:
        """List all available tools from the server."""
        if not self.session:
            print("Not connected to server.")
            return

        print("Available tools:")
        print("-" * 80)

        tools_result = await self.session.list_tools()

        if not tools_result.tools:
            print("No tools available.")
            return

        for tool in tools_result.tools:
            print(f"tool: {tool.name}")
            if tool.description:
                print(f"description: {tool.description}")
            if tool.inputSchema:
                # Show parameters
                properties = tool.inputSchema.get("properties", {})
                if properties:
                    print("parameters:")
                    for param_name, param_info in properties.items():
                        param_type = param_info.get("type", "any")
                        param_desc = param_info.get("description", "")
                        print(f"     - {param_name} ({param_type}): {param_desc}")
            print()

        print("-" * 80)

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool with given arguments."""
        if not self.session:
            print("Not connected to server.")
            return None

        try:
            result = await self.session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            print(f"Error calling tool '{tool_name}': {e}")
            return None

    async def interactive_loop(self) -> None:
        """Run interactive REPL for testing tools."""
        print("\nInteractive MCP Test Client")
        print("=" * 80)
        print("\nCommands:")
        print("  browse [path]       - Browse tools at given path (empty for root)")
        print(
            "  execute             - Execute a multi-line script (finish with two Enter)"
        )
        print("  last                - Re-execute the last script")
        print("  list                - List all available tools")
        print("  help                - Show this help message")
        print("  exit                - Exit the client")
        print("\n" + "=" * 80 + "\n")

        # Show history status
        if self.last_script:
            print(f"📝 Script history loaded from {self.HISTORY_FILE}")
            print("   Use 'execute' and arrow-up to recall\n")

        # List tools on startup
        await self.list_tools()

        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                # Parse command
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                if command == "exit":
                    print("Exiting...")
                    break

                elif command == "help":
                    print("\nCommands:")
                    print("  browse [path]       - Browse tools at given path")
                    print(
                        "  execute             - Execute a multi-line script (finish with two Enter)"
                    )
                    print("  last                - Re-execute the last script")
                    print("  list                - List all available tools")
                    print("  help                - Show this help message")
                    print("  exit                - Exit the client")

                elif command == "list":
                    await self.list_tools()

                elif command == "last":
                    if not self.last_script:
                        print("No script history found. Run 'execute' first.")
                        continue

                    print(f"\nRe-executing last script:\n{self.last_script}\n")
                    result = await self.call_tool(
                        "execute_script", {"script": self.last_script}
                    )
                    if result:
                        print("\nResult:")
                        for content in result.content:
                            if hasattr(content, "text"):
                                print(content.text)

                elif command == "browse":
                    path = args.strip()
                    print(f"\nBrowsing path: '{path}'")
                    result = await self.call_tool("browse_tools", {"path": path})
                    if result:
                        print("\nResult:")
                        for content in result.content:
                            if hasattr(content, "text"):
                                print(content.text)

                elif command == "execute":
                    # Multi-line script input mode
                    print("Your script (will be executed by two <enter>):")
                    if self.last_script:
                        print("(Tip: Arrow-up to recall previous script)")

                    # Save current readline history and set up script history
                    saved_history = []
                    if readline:
                        # Save current history
                        hist_len = readline.get_current_history_length()
                        for i in range(1, hist_len + 1):
                            saved_history.append(readline.get_history_item(i))

                        # Clear history and add last script lines in REVERSE order
                        # This way arrow-up shows line 1 first, then line 2, etc.
                        readline.clear_history()
                        if self.last_script:
                            script_lines = self.last_script.split("\n")
                            for line in reversed(script_lines):
                                readline.add_history(line)

                    lines = []
                    empty_line_count = 0

                    try:
                        while True:
                            try:
                                line = input()

                                if line == "":
                                    empty_line_count += 1
                                    if empty_line_count >= 2:
                                        break
                                    lines.append(line)
                                else:
                                    empty_line_count = 0
                                    lines.append(line)

                            except EOFError:
                                break

                    finally:
                        # Restore original history
                        if readline:
                            readline.clear_history()
                            for hist_item in saved_history:
                                if hist_item:
                                    readline.add_history(hist_item)

                    # Remove trailing empty lines
                    while lines and lines[-1] == "":
                        lines.pop()

                    if not lines:
                        print("No script provided.")
                        continue

                    script = "\n".join(lines)
                    self.last_script = script  # Store for next time
                    self._save_last_script()  # Persist to disk BEFORE execution (for error recovery)

                    print("\nExecuting script...")
                    result = await self.call_tool("execute_script", {"script": script})
                    if result:
                        print("\nResult:")
                        for content in result.content:
                            if hasattr(content, "text"):
                                print(content.text)

                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Type 'exit' to quit.")
            except EOFError:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive MCP test client for switchboard_mcp server"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport to use for connecting to server (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Server host for HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port for HTTP transport (default: 8000)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0,
        help="Delay in seconds before connecting to server (default: 0)",
    )

    args = parser.parse_args()

    client = MCPTestClient(
        transport=args.transport,
        host=args.host,
        port=args.port,
    )

    try:
        if args.delay > 0:
            print(f"Waiting {args.delay} seconds before connecting...")
            await asyncio.sleep(args.delay)

        await client.connect()
        await client.interactive_loop()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        await client.disconnect()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
