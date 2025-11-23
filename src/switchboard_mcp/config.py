from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import yaml
from mcp import StdioServerParameters


@dataclass
class StdioConfig:
    command: str
    args: list[str]
    env: Optional[dict[str, str]] = None

    def to_params(self) -> StdioServerParameters:
        return StdioServerParameters(command=self.command, args=self.args, env=self.env)


@dataclass
class SSEConfig:
    url: str
    headers: Optional[dict[str, str]] = None
    timeout: Optional[float] = None


@dataclass
class NamespaceMapping:
    """Defines how to map tool name patterns to modules.

    Supports glob-like patterns:
    - name* : matches tools starting with 'name'
    - *name : matches tools ending with 'name'
    - *name* : matches tools containing 'name'
    """
    tools: list[str]
    namespace: str


@dataclass
class MCPServerConfig:
    name: str
    stdio: Optional[StdioConfig] = None
    sse: Optional[SSEConfig] = None
    namespace_mappings: Optional[list[NamespaceMapping]] = None
    remove_prefix: Optional[str] = None

    def __post_init__(self):
        if not self.stdio and not self.sse:
            raise ValueError("Either stdio or sse must be configured")
        if self.stdio and self.sse:
            raise ValueError("Only one transport can be configured")

    @classmethod
    def from_yaml(cls, yaml_path: str) -> list[MCPServerConfig]:
        """Load MCP server configurations from YAML file."""
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        servers = []
        for server_data in data["servers"]:
            # Parse stdio config if present
            stdio = None
            if "stdio" in server_data:
                stdio = StdioConfig(**server_data["stdio"])

            # Parse sse config if present
            sse = None
            if "sse" in server_data:
                sse = SSEConfig(**server_data["sse"])

            # Parse module mappings if present
            namespace_mappings = None
            if "namespace_mappings" in server_data:
                namespace_mappings = [
                    NamespaceMapping(**mapping)
                    for mapping in server_data["namespace_mappings"]
                ]

            # Parse remove_prefix if present
            remove_prefix = server_data.get("remove_prefix")

            # Create server config
            config = MCPServerConfig(
                name=server_data["name"],
                stdio=stdio,
                sse=sse,
                namespace_mappings=namespace_mappings,
                remove_prefix=remove_prefix,
            )
            servers.append(config)

        return servers
