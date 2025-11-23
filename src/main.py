from __future__ import annotations

import asyncio
import os
import random
from typing import Any

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

import src.switchboard_mcp.utils as utils
from simple_script.interpreter import Interpreter
from simple_script.tools import Tool
from switchboard_mcp.utils import Folder

load_dotenv()


AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AGENT_MODEL = os.environ.get("AGENT_MODEL", "")


client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=AZURE_OPENAI_API_KEY,
)

model = (
    OpenAIResponsesModel(
        AGENT_MODEL,
        provider=OpenAIProvider(openai_client=client),
    )
    if "codex" in AGENT_MODEL
    else OpenAIChatModel(
        AGENT_MODEL,
        provider=OpenAIProvider(openai_client=client),
    )
)


class Services:
    def __init__(self, tools: list[Tool] | None = None):
        if tools is None:
            tools = []
        self.root = Folder.from_tools(tools)
        self.tools = tools


def math_operations_plus(x: float, y: float) -> float:
    """Add two numbers together.

    Args:
        x: The first number
        y: The second number
    """
    return x + y


def math_operations_minus(x: float, y: float) -> float:
    """Subtract the second number from the first.

    Args:
        x: The first number
        y: The second number
    """
    return x - y


def math_operations_multiply(x: float, y: float) -> float:
    """Multiply two numbers.

    Args:
        x: The first number
        y: The second number
    """
    return x * y


def math_operations_divide(x: float, y: float) -> float:
    """Divide the first number by the second.

    Args:
        x: The numerator
        y: The denominator
    """
    return x / y


def math_statistics_min(numbers: list[float]) -> float:
    """Find the minimum value in a list of numbers.

    Args:
        numbers: List of numbers to find the minimum from
    """
    return min(numbers)


def math_statistics_max(numbers: list[float]) -> float:
    """Find the maximum value in a list of numbers.

    Args:
        numbers: List of numbers to find the maximum from
    """
    return max(numbers)


def math_statistics_average(numbers: list[float]) -> float:
    """Calculate the average (mean) of a list of numbers.

    Args:
        numbers: List of numbers to calculate the average from
    """
    return sum(numbers) / len(numbers)


def math_random_generate_list(n: int, start: float, end: float) -> list[float]:
    """Generate a list of random floating-point numbers.

    Args:
        n: The number of random values to generate
        start: The minimum value (inclusive)
        end: The maximum value (inclusive)
    """
    return [random.uniform(start, end) for _ in range(n)]


math_mcp = [
    Tool.from_function(math_operations_plus),
    Tool.from_function(math_operations_minus),
    Tool.from_function(math_operations_multiply),
    Tool.from_function(math_operations_divide),
    Tool.from_function(math_statistics_min),
    Tool.from_function(math_statistics_max),
    Tool.from_function(math_statistics_average),
    Tool.from_function(math_random_generate_list),
]


tools = [*math_mcp]


def browse_tools(ctx: RunContext[Services], path: str = "") -> str:
    """
    Browse tools organized in a hierarchical structure using dot notation.
    Shows submodules and functions with their parameters and descriptions.


    Args:
        path: Dot-separated path (e.g., "module1.submodule2")
              Empty string or no argument lists root level - that should be the first thing to check

    Returns:
        String with submodules listed first, then functions with parameters and descriptions
    """

    print(f"browse_tools(path: '{path}')")
    result = utils.browse_tools(ctx.deps.root, path)
    print(f"browse_tools result:\n{result}\n")
    return result


def execute_script(ctx: RunContext[Services], script: str) -> str:
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

    print("execute_script -------------------------- START")
    print(script)
    prints = []

    def builtins_print(*args: Any) -> None:
        """Print all arguments."""
        output = " ".join(str(arg) for arg in args)
        prints.append(output)

    interpreter = Interpreter(
        tools=[*ctx.deps.tools, Tool.from_function(builtins_print)]
    )
    _ = interpreter.evaluate(script)
    print("execute_script -------------------------- END")
    result = "\n".join(prints)
    print(result)
    print("")
    return result


agent = Agent(
    model=model,
    deps_type=Services,
    retries=2,
    model_settings=ModelSettings(
        parallel_tool_calls=True,
    ),
    tools=[browse_tools, execute_script],
    instructions="""
You are an student assistant, all calculations MUST be done with tools, the logic these tools provides is a different from what have you been learn.

You have available extraordinary tool which is repository of different modules that can be explored with browse_tools tool.
You can use these tools to execute the script with execute_script tool.
""",
)


async def main():
    history = []
    result = await agent.run("What is 5 plus 3?", deps=Services(tools=tools))
    history += result.new_messages()
    print(result.output)
    result = await agent.run(
        "What is 5 minus 3?",
        deps=Services(tools=tools),
        message_history=history,
    )
    history.append(result.new_messages())
    print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
