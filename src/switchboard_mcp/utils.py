from __future__ import annotations

import asyncio
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from simple_script.interpreter import Interpreter
from simple_script.tools import Tool


@dataclass
class Folder:
    name: str
    folders: list["Folder"]
    tools: list[Tool]

    @classmethod
    def from_tools(cls, tools: list[Tool]) -> "Folder":
        """Build a hierarchical folder structure with 3+ grouping rule.

        Only creates subfolders when 3 or more tools share the same prefix.
        Tools with < 3 items in their group are flattened to the parent level.
        """
        root = cls(name="", folders=[], tools=[])

        # Separate builtin tools from regular tools
        builtins = []
        regular_tools = []
        for tool in tools:
            if tool.name.startswith("builtins_"):
                builtins.append(tool)
            else:
                regular_tools.append(tool)

        # Add builtins directly to root
        root.tools.extend(builtins)

        # Group regular tools by first part (always create top-level folders)
        top_groups = defaultdict(list)
        for tool in regular_tools:
            parts = tool.name.split("_")
            if len(parts) == 1:
                # Single-part name, add as tool
                root.tools.append(tool)
            else:
                first_part = parts[0]
                top_groups[first_part].append(tool)

        # Create top-level folders and recursively process with grouping rules
        for folder_name, folder_tools in top_groups.items():
            subfolder = cls(name=folder_name, folders=[], tools=[])
            root.folders.append(subfolder)
            _add_tools_with_grouping(subfolder, folder_tools, 1)

        return root


def _add_tools_with_grouping(folder: Folder, tools: list[Tool], depth: int) -> None:
    """Recursively add tools to folder, applying 3+ grouping rule.

    Args:
        folder: The folder to add tools to
        tools: List of tools to process
        depth: Current depth in the tool name hierarchy (0-indexed)
    """
    if not tools:
        return

    # Group tools by the next part in their name
    groups = defaultdict(list)

    for tool in tools:
        parts = tool.name.split("_")
        if depth >= len(parts) - 1:
            # This is a leaf tool at this level (no more parts)
            folder.tools.append(tool)
        else:
            next_part = parts[depth]
            groups[next_part].append(tool)

    # Process each group with the 3+ rule
    for group_name, group_tools in groups.items():
        if len(group_tools) >= 3:
            # Create subfolder for this group (3+ tools)
            subfolder = Folder(name=group_name, folders=[], tools=[])
            folder.folders.append(subfolder)
            _add_tools_with_grouping(subfolder, group_tools, depth + 1)
        else:
            # Flatten: skip this level, add tools directly to current folder
            folder.tools.extend(group_tools)


def copy_doc(from_func):
    def decorator(to_func):
        to_func.__doc__ = from_func.__doc__
        return to_func

    return decorator


def _format_function_description(tool: Tool) -> str:
    """
    Format a tool as a function signature with description.

    Args:
        tool: The Tool object to format

    Returns:
        Formatted string: "function_name(param1: type1, param2: type2): description"
    """
    # Extract function name from the tool name
    # For builtins, strip the "builtins_" prefix
    if tool.name.startswith("builtins_"):
        function_name = tool.name[len("builtins_") :]
    else:
        # For regular tools, use last part after splitting by _
        function_name = tool.name.split("_")[-1]

    # Build parameter signature
    if tool.parameters:
        param_strs = []
        for param in tool.parameters:
            if param.type:
                param_strs.append(f"{param.name}: {param.type}")
            else:
                param_strs.append(param.name)
        param_signature = f"({', '.join(param_strs)})"
    else:
        param_signature = "()"

    return f"{function_name}{param_signature}: {tool.description}"


def _format_type_from_schema(schema: dict[str, Any], type_name: str) -> str:
    """
    Convert JSON Schema to Python TypedDict class syntax.

    Args:
        schema: JSON Schema dictionary (typically from inputSchema)
        type_name: Name for the generated type

    Returns:
        Formatted TypedDict class definition string
    """
    if schema.get("type") != "object":
        # Not an object type, skip
        return ""

    properties = schema.get("properties", {})
    if not properties:
        return ""

    required_fields = set(schema.get("required", []))

    lines = [f"class {type_name}Dict(TypedDict):"]

    for prop_name, prop_schema in properties.items():
        prop_type = _json_type_to_python(prop_schema)

        # Mark optional fields with NotRequired if not in required list
        if prop_name not in required_fields:
            prop_type = f"NotRequired[{prop_type}]"

        lines.append(f"    {prop_name}: {prop_type}")

    return "\n".join(lines)


def _extract_nested_types(schema: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """
    Extract nested complex types from a JSON Schema root.

    Only extracts object types from direct properties and array items.
    Does not extract the root schema itself (which is represented by function parameters).

    Args:
        schema: JSON Schema dictionary (typically from tool.inputSchema)

    Returns:
        List of (type_name, schema) tuples for nested object types to be formatted as TypedDict
    """
    nested_types = []

    if schema.get("type") != "object":
        return nested_types

    properties = schema.get("properties", {})

    for prop_name, prop_schema in properties.items():
        # Capitalize property name for type name
        type_name = prop_name[0].upper() + prop_name[1:] if prop_name else prop_name

        if prop_schema.get("type") == "object":
            # Direct nested object property
            nested_types.append((type_name, prop_schema))

        elif prop_schema.get("type") == "array":
            # Check if array items are objects
            items = prop_schema.get("items", {})
            if isinstance(items, dict) and items.get("type") == "object":
                # Array of objects - use property name for the item type
                nested_types.append((type_name, items))

    return nested_types


def _json_type_to_python(schema: dict[str, Any]) -> str:
    """
    Convert JSON Schema type to Python type annotation.

    Args:
        schema: JSON Schema for a single property

    Returns:
        Python type string (e.g., 'str', 'int', 'list[str]', 'Literal["a", "b"]')
    """
    json_type = schema.get("type")

    # Handle enum as Literal
    if "enum" in schema:
        enum_values = schema["enum"]
        # Format string values with quotes
        formatted_values = [f'"{v}"' if isinstance(v, str) else str(v) for v in enum_values]
        return f"Literal[{', '.join(formatted_values)}]"

    # Handle basic types
    if json_type == "string":
        return "str"
    elif json_type == "integer":
        return "int"
    elif json_type == "number":
        return "float"
    elif json_type == "boolean":
        return "bool"
    elif json_type == "array":
        items = schema.get("items", {})
        if items:
            item_type = _json_type_to_python(items)
            return f"list[{item_type}]"
        return "list[Any]"
    elif json_type == "object":
        # Nested object - would need recursive handling
        return "dict[str, Any]"

    return "Any"


def browse_tools(root: Folder, path: str = "") -> str:
    """
    Browse tools organized in a hierarchical structure using dot notation.
    Shows subnamespaces and functions with their parameters and descriptions.

    Args:
        path: Dot-separated path (e.g., "math.statistics")
              Empty string or no argument lists root level

    Returns:
        String with subnamespaces listed first, then functions with parameters and descriptions
    """

    parts = [i for i in path.split(".") if i != ""]
    current_folder = root

    for part in parts:
        folder = next((f for f in current_folder.folders if f.name == part), None)
        if not folder:
            return f"Path '{path}' not found."
        current_folder = folder

    # Build full paths for subnamespaces with counts
    current_path = path if path else ""
    subnamespaces = []
    for f in current_folder.folders:
        if current_path:
            full_path = f"{current_path}.{f.name}"
        else:
            full_path = f.name

        # Count subnamespaces and functions in this folder
        num_subnamespaces = len(f.folders)
        num_functions = len(f.tools)

        subnamespaces.append((full_path, num_subnamespaces, num_functions))

    result_parts = []

    # 1. Show subnamespaces with counts
    if subnamespaces:
        result_parts.append("Subnamespaces:")
        for ns_path, num_sub, num_func in subnamespaces:
            result_parts.append(f"  {ns_path} (subnamespaces: {num_sub}, functions: {num_func})")

    # 2. Show types (only nested types from inputSchema, not root types)
    types_to_show = []
    for tool in current_folder.tools:
        if tool.inputSchema:
            # Extract nested types from the inputSchema (not the root itself)
            nested_types = _extract_nested_types(tool.inputSchema)
            for type_name, type_schema in nested_types:
                type_def = _format_type_from_schema(type_schema, type_name)
                if type_def:
                    types_to_show.append(type_def)

    if types_to_show:
        if result_parts:
            result_parts.append("")  # Empty line separator
        result_parts.append("Types:")
        for type_def in types_to_show:
            # Indent each line of the type definition
            indented = "\n".join(f"  {line}" for line in type_def.split("\n"))
            result_parts.append(indented)

    # 3. Show functions
    if current_folder.tools:
        if result_parts:
            result_parts.append("")  # Empty line separator
        result_parts.append("Functions:")
        for tool in current_folder.tools:
            result_parts.append(f"  {_format_function_description(tool)}")

    return "\n".join(result_parts) if result_parts else "No entries found."


def _execute_script_sync(tools: list[Tool], script: str) -> str:
    """Synchronous script execution - runs in a separate thread."""
    print("execute_script -------------------------- START")
    print(script)
    prints = []

    def builtins_print(*args: Any) -> None:
        """Print all arguments."""
        output = " ".join(str(arg) for arg in args)
        prints.append(output)

    interpreter = Interpreter(tools=[*tools, Tool.from_function(builtins_print)])
    _ = interpreter.evaluate(script)
    print("execute_script -------------------------- END")
    result = "\n".join(prints)
    print(result)
    print("")
    return result


async def execute_script(tools: list[Tool], script: str) -> str:
    """
    This is super simple python executor.
    It supports only:
    - imports with from ... import ... ...
    - function calls with positional arguments only
    - simple print statement

    Example:
    ```python
        from math.operations import plus, minus
        result = plus(2, 3)
        print(result)
    ```
    """
    # Run the script in a separate thread so that tools can use
    # asyncio.run_coroutine_threadsafe to call back to this event loop
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, _execute_script_sync, tools, script)
    return result
