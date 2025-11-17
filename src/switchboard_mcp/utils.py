from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from simple_script.interpreter import Interpreter
from simple_script.tools import Tool

if TYPE_CHECKING:
    from switchboard_mcp.session_manager import ToolGroup


@dataclass
class Folder:
    name: str
    folders: list["Folder"]
    tools: list[Tool]

    @classmethod
    def from_tools(cls, tool_groups: list[ToolGroup]) -> Folder:
        """Build a hierarchical folder structure from tool groups with namespace mappings.

        For each tool:
        - Tools starting with 'builtins_' are added directly to root
        - Tools matching a namespace mapping pattern are placed under: server_name.namespace.remaining
          Patterns support: name* (prefix), *name (suffix), *name* (contains)
        - Tools not matching any mapping are placed under: server_name.tool_name
        """
        root = cls(name="", folders=[], tools=[])

        for tool_group in tool_groups:
            server_name = tool_group.server_config.name
            remove_prefix = tool_group.server_config.remove_prefix

            for tool in tool_group.tools:
                # Handle builtins - always add directly to root
                if tool.name.startswith("builtins_"):
                    root.tools.append(tool)
                    continue

                # Apply prefix removal if configured
                tool_to_add = tool
                if remove_prefix and tool.name.startswith(remove_prefix):
                    # Create a new tool with the prefix removed from the name
                    new_name = tool.name[len(remove_prefix):]
                    tool_to_add = Tool(
                        name=new_name,
                        func=tool.func,
                        description=tool.description,
                        parameters=tool.parameters,
                        inputSchema=tool.inputSchema,
                    )

                # Try to apply namespace mappings
                mapped = False
                if tool_group.server_config.namespace_mappings:
                    for mapping in tool_group.server_config.namespace_mappings:
                        # Try each pattern in the mapping
                        # Use original tool name for pattern matching
                        for pattern in mapping.tools:
                            if _match_pattern(tool.name, pattern):
                                # Split namespace by dots to create folder hierarchy
                                namespace_parts = mapping.namespace.split(".")
                                # Prepend server name to namespace path
                                full_path = [server_name] + namespace_parts

                                # Navigate/create folder hierarchy and add tool (with prefix removed if configured)
                                _add_tool_to_path(root, full_path, tool_to_add)
                                mapped = True
                                break

                        if mapped:
                            break

                # If no mapping matched, add directly to server folder
                if not mapped:
                    full_path = [server_name]
                    _add_tool_to_path(root, full_path, tool_to_add)

        return root


def _match_pattern(tool_name: str, pattern: str) -> bool:
    """Match a tool name against a glob-like pattern.

    Supports three pattern types:
    - name*  : matches tools starting with 'name'
    - *name  : matches tools ending with 'name'
    - *name* : matches tools containing 'name'

    Args:
        tool_name: The tool name to match
        pattern: The glob pattern

    Returns:
        True if the pattern matches, False otherwise
    """
    if "*" not in pattern:
        # Exact match (no wildcard)
        return tool_name == pattern

    # Count wildcards
    wildcard_count = pattern.count("*")
    if wildcard_count > 2:
        return False

    # Handle different pattern types
    if pattern.startswith("*") and pattern.endswith("*"):
        # *name* - contains pattern
        if wildcard_count != 2:
            return False
        search_str = pattern[1:-1]  # Remove both asterisks
        return search_str in tool_name

    elif pattern.startswith("*"):
        # *name - suffix pattern (tool ends with name)
        suffix = pattern[1:]  # Remove asterisk
        return tool_name.endswith(suffix)

    elif pattern.endswith("*"):
        # name* - prefix pattern (tool starts with name)
        prefix = pattern[:-1]  # Remove asterisk
        return tool_name.startswith(prefix)

    return False


def _add_tool_to_path(root: Folder, path: list[str], tool: Tool) -> None:
    """Navigate/create folder hierarchy and add tool at the end.

    Args:
        root: The root folder to start from
        path: List of folder names (e.g., ['server_name', 'namespace'])
        tool: The tool to add (keeps its original full name)
    """
    if not path:
        root.tools.append(tool)
        return

    # Navigate/create all folders in the path
    current_folder = root
    for part in path:
        # Find or create subfolder
        subfolder = next((f for f in current_folder.folders if f.name == part), None)
        if not subfolder:
            subfolder = Folder(name=part, folders=[], tools=[])
            current_folder.folders.append(subfolder)
        current_folder = subfolder

    # Add the tool to the final folder (tool keeps its original name)
    current_folder.tools.append(tool)


def copy_doc(from_func):
    def decorator(to_func):
        to_func.__doc__ = from_func.__doc__
        return to_func

    return decorator


def _format_function_description(tool: Tool) -> str:
    """
    Format a tool as a Python function definition with type hints.

    Args:
        tool: The Tool object to format

    Returns:
        Formatted multi-line Python function definition string
    """
    import inspect

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

    # Determine return type
    return_type = "Any"
    if tool.func:
        try:
            # Try to get return annotation from the function
            sig = inspect.signature(tool.func)
            if sig.return_annotation != inspect.Signature.empty:
                # Get the string representation of the return type
                return_annotation = sig.return_annotation
                if hasattr(return_annotation, "__name__"):
                    return_type = return_annotation.__name__
                else:
                    return_type = str(return_annotation).replace("typing.", "")
        except Exception:
            # If we can't inspect, default to Any
            return_type = "Any"

    # Format as Python function definition
    lines = []
    lines.append(f"def {function_name}{param_signature} -> {return_type}:")
    lines.append(f'    """{tool.description}"""')
    lines.append("    ...")

    return "\n".join(lines)


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
        formatted_values = [
            f'"{v}"' if isinstance(v, str) else str(v) for v in enum_values
        ]
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
        result_parts.append("Namespaces:")
        for ns_path, num_sub, num_func in subnamespaces:
            result_parts.append(
                f"  {ns_path} (subnamespaces: {num_sub}, functions: {num_func})"
            )

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
            # Indent each line of the function definition
            func_def = _format_function_description(tool)
            indented = "\n".join(f"  {line}" for line in func_def.split("\n"))
            result_parts.append(indented)

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
    Python-like interpreter. Supports: imports, variables, literals (str/int/list/dict),
    operators (+,-,*,/,==,<,>), if/else, while, def/return, print().

    Example:
    ```python
        from math.operations import plus
        print(plus(2, 3))
    ```
    """
    # Run the script in a separate thread so that tools can use
    # asyncio.run_coroutine_threadsafe to call back to this event loop
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor, _execute_script_sync, tools, script
        )
    return result
