from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pydantic_ai import Tool as PydanticTool


@dataclass
class ToolParameter:
    name: str
    type: str | None = None  # Optional type annotation


@dataclass
class Tool:
    name: str
    func: Callable[..., Any] | None
    description: str
    parameters: list[ToolParameter] | None = None
    inputSchema: dict[str, Any] | None = None  # Full JSON schema for complex types

    @classmethod
    def from_function(cls, func: Callable[..., Any]) -> Tool:
        """Create a Tool from a function using pydantic-ai introspection."""
        pydantic_tool = PydanticTool(func, takes_ctx=False)

        # Extract parameters from JSON schema
        parameters = []
        json_schema = pydantic_tool.function_schema.json_schema
        if "properties" in json_schema:
            for param_name, param_schema in json_schema["properties"].items():
                param_type = param_schema.get("type", None)
                # Handle array types
                if param_type == "array":
                    items_type = param_schema.get("items", {}).get("type", "any")
                    param_type = f"list[{items_type}]"
                parameters.append(ToolParameter(name=param_name, type=param_type))

        return cls(
            name=pydantic_tool.name,
            func=func,
            description=pydantic_tool.description or "No description available",
            parameters=parameters if parameters else None,
        )

    @classmethod
    def from_mcp_tool(cls, mcp_tool: Any, func: Callable[..., Any]) -> Tool:
        """Create a Tool from an MCP tool object."""
        # Extract parameters from inputSchema
        parameters = []
        input_schema = None
        if hasattr(mcp_tool, "inputSchema") and mcp_tool.inputSchema:
            input_schema = mcp_tool.inputSchema
            properties = input_schema.get("properties", {})
            for param_name, param_schema in properties.items():
                param_type = param_schema.get("type", None)
                # Handle array types
                if param_type == "array":
                    items = param_schema.get("items", {})
                    items_type = (
                        items.get("type", "any") if isinstance(items, dict) else "any"
                    )
                    param_type = f"list[{items_type}]"
                parameters.append(ToolParameter(name=param_name, type=param_type))

        return cls(
            name=mcp_tool.name,
            func=func,
            description=mcp_tool.description or "No description available",
            parameters=parameters if parameters else None,
            inputSchema=input_schema,
        )
