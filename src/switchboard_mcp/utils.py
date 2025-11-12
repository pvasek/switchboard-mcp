from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from simple_script.interpreter import Interpreter
from simple_script.tools import Folder, Tool


def copy_doc(from_func):
    def decorator(to_func):
        to_func.__doc__ = from_func.__doc__
        return to_func

    return decorator


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

    # Build full paths for subnamespaces
    current_path = path if path else ""
    subnamespaces = []
    for f in current_folder.folders:
        if current_path:
            full_path = f"{current_path}.{f.name}"
        else:
            full_path = f.name
        subnamespaces.append(full_path)

    result_parts = []
    if subnamespaces:
        result_parts.append("Subnamespaces:")
        result_parts.extend(f"  {ns}" for ns in subnamespaces)

    if current_folder.tools:
        if result_parts:
            result_parts.append("")  # Empty line separator
        result_parts.append("Functions:")
        for tool in current_folder.tools:
            # Extract function name from the tool name
            # For builtins, strip the "builtins_" prefix
            if tool.name.startswith("builtins_"):
                function_name = tool.name[len("builtins_") :]
            else:
                # For regular tools, use last part after splitting by _
                function_name = tool.name.split("_")[-1]
            description = tool.description

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

            result_parts.append(f"  {function_name}{param_signature}: {description}")

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
