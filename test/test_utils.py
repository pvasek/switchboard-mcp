import pytest
from src.utils import browse_tools, Services, Tool


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


@pytest.fixture
def services():
    """Fixture to provide Services instance with mock math tools for testing."""
    # Mock math_mcp tools structure using Tool.from_function
    mock_tools = [
        Tool.from_function(math_operations_plus),
        Tool.from_function(math_operations_minus),
        Tool.from_function(math_operations_multiply),
        Tool.from_function(math_operations_divide),
        Tool.from_function(math_statistics_min),
        Tool.from_function(math_statistics_max),
        Tool.from_function(math_statistics_average),
    ]
    return Services(tools=mock_tools)


class TestBrowseTools:
    """Test suite for the browse_tools function."""

    def test_browse_tools_root(self, services):
        """Test browsing root level (empty string)."""
        result = browse_tools(services, "")
        assert "Subnamespaces:" in result
        assert "  math" in result
        # Root should only have subnamespaces, no functions
        assert "Functions:" not in result

    def test_browse_tools_root_no_arg(self, services):
        """Test browsing root level with no argument."""
        result = browse_tools(services)
        assert "Subnamespaces:" in result
        assert "  math" in result

    def test_browse_tools_math(self, services):
        """Test browsing math namespace."""
        result = browse_tools(services, "math")
        assert "Subnamespaces:" in result
        assert "  math.operations" in result
        assert "  math.statistics" in result
        # Math level should only have subnamespaces
        assert "Functions:" not in result

    def test_browse_tools_math_statistics(self, services):
        """Test browsing math.statistics with descriptions and parameters."""
        result = browse_tools(services, "math.statistics")

        # Should have Functions section with parameters and types
        assert "Functions:" in result
        assert "  min(numbers: list[number]): Find the minimum value in a list of numbers" in result
        assert "  max(numbers: list[number]): Find the maximum value in a list of numbers" in result
        assert "  average(numbers: list[number]): Calculate the average (mean) of a list of numbers" in result

        # Should NOT have Subnamespaces section
        assert "Subnamespaces:" not in result

    def test_browse_tools_math_operations(self, services):
        """Test browsing math.operations with descriptions and parameters."""
        result = browse_tools(services, "math.operations")

        # Should have Functions section with parameters, types, and descriptions
        assert "Functions:" in result
        assert "  plus(x: number, y: number): Add two numbers together" in result
        assert "  minus(x: number, y: number): Subtract the second number from the first" in result
        assert "  multiply(x: number, y: number): Multiply two numbers" in result
        assert "  divide(x: number, y: number): Divide the first number by the second" in result

        # Should NOT have Subnamespaces section
        assert "Subnamespaces:" not in result

    def test_browse_tools_notexists(self, services):
        """Test browsing non-existent path."""
        result = browse_tools(services, "notexists")
        assert result == "Path 'notexists' not found."

    def test_browse_tools_nested_notexists(self, services):
        """Test browsing non-existent nested path."""
        result = browse_tools(services, "math.notexists")
        assert result == "Path 'math.notexists' not found."

    def test_browse_tools_separator_difference(self, services):
        """Test that browse_tools uses dots, not slashes."""
        # This should work
        result_dot = browse_tools(services, "math.statistics")
        assert "Functions:" in result_dot

        # This should not work (verifying it's truly dot-based)
        result_slash = browse_tools(services, "math/statistics")
        assert "not found" in result_slash

    def test_browse_tools_with_builtins_at_root(self):
        """Test that builtin tools appear directly in root folder."""
        def builtin_print(text: str) -> str:
            """Print text to output."""
            return f"printed: {text}"

        def builtin_template(template: str, data: str) -> str:
            """Render a liquid template."""
            return f"{template}: {data}"

        def math_operations_plus(x: float, y: float) -> float:
            """Add two numbers."""
            return x + y

        # Create tools including builtins
        tools = [
            Tool.from_function(builtin_print),
            Tool.from_function(builtin_template),
            Tool.from_function(math_operations_plus),
        ]
        # Manually set names to simulate how they would be named
        tools[0].name = "builtins_print"
        tools[1].name = "builtins_liquid_template_as_str"
        tools[2].name = "math_operations_plus"

        services = Services(tools=tools)
        result = browse_tools(services, "")

        # Should have both Subnamespaces and Functions at root
        assert "Subnamespaces:" in result
        assert "  math" in result

        assert "Functions:" in result
        assert "  print(text: string): Print text to output" in result
        assert "  liquid_template_as_str(template: string, data: string): Render a liquid template" in result

    def test_browse_tools_builtins_and_regular_mix(self):
        """Test that builtins at root don't interfere with regular nested tools."""
        def builtin_print(text: str) -> str:
            """Print text."""
            return f"printed: {text}"

        def math_statistics_min(numbers: list[float]) -> float:
            """Find minimum."""
            return min(numbers)

        tools = [
            Tool.from_function(builtin_print),
            Tool.from_function(math_statistics_min),
        ]
        tools[0].name = "builtins_print"
        tools[1].name = "math_statistics_min"

        services = Services(tools=tools)

        # Check root
        root_result = browse_tools(services, "")
        assert "Subnamespaces:" in root_result
        assert "  math" in root_result
        assert "Functions:" in root_result
        assert "  print(text: string): Print text" in root_result

        # Check math.statistics still works
        math_stats_result = browse_tools(services, "math.statistics")
        assert "Functions:" in math_stats_result
        assert "  min(numbers: list[number]): Find minimum" in math_stats_result
        assert "Subnamespaces:" not in math_stats_result
