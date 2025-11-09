import pytest
from src.simple_script import Interpreter, Tool


def test_interpreter_evaluates_simple_number():
    """Test evaluating a simple number expression"""
    interpreter = Interpreter([])
    result = interpreter.evaluate("42")
    assert result == 42


def test_interpreter_evaluates_arithmetic():
    """Test evaluating basic arithmetic"""
    interpreter = Interpreter([])
    result = interpreter.evaluate("5 + 3")
    assert result == 8


def test_interpreter_evaluates_variable_assignment():
    """Test variable assignment and retrieval"""
    interpreter = Interpreter([])
    script = """x = 10
x"""
    result = interpreter.evaluate(script)
    assert result == 10


def test_interpreter_calls_tool_function():
    """Test calling a tool function"""
    def add_func(x: float, y: float) -> float:
        """Add two numbers."""
        return x + y

    add_tool = Tool.from_function(add_func)
    add_tool.name = "math_operations_plus"

    interpreter = Interpreter([add_tool])
    script = """from math.operations import plus
result = plus(5, 3)
result"""

    result = interpreter.evaluate(script)
    assert result == 8


def test_interpreter_calls_multiple_tools():
    """Test calling multiple tool functions"""
    def add_func(x: float, y: float) -> float:
        """Add two numbers."""
        return x + y

    def multiply_func(x: float, y: float) -> float:
        """Multiply two numbers."""
        return x * y

    add_tool = Tool.from_function(add_func)
    add_tool.name = "math_operations_plus"

    multiply_tool = Tool.from_function(multiply_func)
    multiply_tool.name = "math_operations_multiply"

    interpreter = Interpreter([add_tool, multiply_tool])
    script = """from math.operations import plus, multiply
result = plus(5, 3)
result2 = multiply(result, 2)
result2"""

    result = interpreter.evaluate(script)
    assert result == 16


def test_interpreter_with_statistics_min():
    """Test calling min function from statistics"""
    def min_func(numbers: list[float]) -> float:
        """Find minimum."""
        return min(numbers)

    min_tool = Tool.from_function(min_func)
    min_tool.name = "math_statistics_min"

    interpreter = Interpreter([min_tool])
    script = """from math.statistics import min
result = min([5, 2, 8, 1, 9])
result"""

    result = interpreter.evaluate(script)
    assert result == 1


def test_interpreter_with_if_statement():
    """Test if statement evaluation"""
    interpreter = Interpreter([])
    script = """x = 10
if x > 5:
    result = 1
else:
    result = 0
result"""

    result = interpreter.evaluate(script)
    assert result == 1


def test_interpreter_with_while_loop():
    """Test while loop evaluation"""
    interpreter = Interpreter([])
    script = """counter = 0
sum = 0
while counter < 5:
    sum = sum + counter
    counter = counter + 1
sum"""

    result = interpreter.evaluate(script)
    assert result == 10


def test_interpreter_import_from_nested_module():
    """Test importing from nested module paths"""
    def avg_func(numbers: list[float]) -> float:
        """Calculate average."""
        return sum(numbers) / len(numbers)

    avg_tool = Tool.from_function(avg_func)
    avg_tool.name = "math_statistics_average"

    interpreter = Interpreter([avg_tool])
    script = """from math.statistics import average
result = average([10, 20, 30])
result"""

    result = interpreter.evaluate(script)
    assert result == 20.0


def test_interpreter_returns_last_expression():
    """Test that interpreter returns the last expression value"""
    interpreter = Interpreter([])
    script = """x = 5
y = 10
x + y"""

    result = interpreter.evaluate(script)
    assert result == 15


def test_interpreter_tool_not_found():
    """Test error when tool is not found"""
    interpreter = Interpreter([])
    script = """from math.operations import plus
plus(5, 3)"""

    with pytest.raises(Exception, match="not found|unknown"):
        interpreter.evaluate(script)


def test_interpreter_builtin_function():
    """Test calling a builtin function without import"""
    def print_func(text: str) -> str:
        """Print text."""
        return f"printed: {text}"

    print_tool = Tool.from_function(print_func)
    print_tool.name = "builtins_print"

    interpreter = Interpreter([print_tool])
    script = """result = print("hello world")
result"""

    result = interpreter.evaluate(script)
    assert result == "printed: hello world"


def test_interpreter_multiple_builtins():
    """Test multiple builtin functions"""
    def print_func(text: str) -> str:
        """Print text."""
        return f"printed: {text}"

    def template_func(template: str, data: str) -> str:
        """Render template."""
        return f"{template}: {data}"

    print_tool = Tool.from_function(print_func)
    print_tool.name = "builtins_print"

    template_tool = Tool.from_function(template_func)
    template_tool.name = "builtins_liquid_template_as_str"

    interpreter = Interpreter([print_tool, template_tool])
    script = """msg = print("hello")
rendered = liquid_template_as_str("name", "John")
rendered"""

    result = interpreter.evaluate(script)
    assert result == "name: John"


def test_interpreter_builtin_and_imported():
    """Test that builtins and imported tools work together"""
    def print_func(text: str) -> str:
        """Print text."""
        return f"printed: {text}"

    def add_func(x: float, y: float) -> float:
        """Add two numbers."""
        return x + y

    print_tool = Tool.from_function(print_func)
    print_tool.name = "builtins_print"

    add_tool = Tool.from_function(add_func)
    add_tool.name = "math_operations_plus"

    interpreter = Interpreter([print_tool, add_tool])
    script = """from math.operations import plus
sum = plus(5, 3)
msg = print("Sum is")
msg"""

    result = interpreter.evaluate(script)
    assert result == "printed: Sum is"


def test_interpreter_imported_overrides_builtin():
    """Test that imported tools take precedence over builtins with same name"""
    def builtin_print(text: str) -> str:
        """Builtin print."""
        return f"builtin: {text}"

    def custom_print(text: str) -> str:
        """Custom print."""
        return f"custom: {text}"

    builtin_tool = Tool.from_function(builtin_print)
    builtin_tool.name = "builtins_print"

    custom_tool = Tool.from_function(custom_print)
    custom_tool.name = "io_print"

    interpreter = Interpreter([builtin_tool, custom_tool])
    script = """from io import print
result = print("test")
result"""

    result = interpreter.evaluate(script)
    assert result == "custom: test"
