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


class TestInterpreterStringSupport:
    """Test interpreter evaluation of strings with single and double quotes"""

    def test_interpreter_evaluates_single_quote_string(self):
        """Test evaluating a single-quoted string"""
        interpreter = Interpreter([])
        result = interpreter.evaluate("'hello'")
        assert result == "hello"

    def test_interpreter_evaluates_double_quote_string(self):
        """Test evaluating a double-quoted string"""
        interpreter = Interpreter([])
        result = interpreter.evaluate('"hello"')
        assert result == "hello"

    def test_interpreter_single_quote_assignment(self):
        """Test assigning a single-quoted string to a variable"""
        interpreter = Interpreter([])
        script = """s = 'world'
s"""
        result = interpreter.evaluate(script)
        assert result == "world"

    def test_interpreter_empty_single_quote_string(self):
        """Test evaluating an empty single-quoted string"""
        interpreter = Interpreter([])
        result = interpreter.evaluate("''")
        assert result == ""

    def test_interpreter_empty_double_quote_string(self):
        """Test evaluating an empty double-quoted string"""
        interpreter = Interpreter([])
        result = interpreter.evaluate('""')
        assert result == ""

    def test_interpreter_single_quote_with_double_quote_inside(self):
        """Test single-quoted string containing double quotes"""
        interpreter = Interpreter([])
        result = interpreter.evaluate("""'He said "hello"'""")
        assert result == 'He said "hello"'

    def test_interpreter_double_quote_with_single_quote_inside(self):
        """Test double-quoted string containing single quotes"""
        interpreter = Interpreter([])
        result = interpreter.evaluate('''"It's working"''')
        assert result == "It's working"

    def test_interpreter_mixed_quotes_in_list(self):
        """Test list with mixed single and double-quoted strings"""
        interpreter = Interpreter([])
        result = interpreter.evaluate("""['single', "double", 'mixed']""")
        assert result == ["single", "double", "mixed"]

    def test_interpreter_single_quote_as_function_argument(self):
        """Test passing single-quoted string to a function"""
        def echo_func(text: str) -> str:
            """Echo text."""
            return f"echo: {text}"

        echo_tool = Tool.from_function(echo_func)
        echo_tool.name = "builtins_echo"

        interpreter = Interpreter([echo_tool])
        script = """result = echo('hello world')
result"""
        result = interpreter.evaluate(script)
        assert result == "echo: hello world"


class TestInterpreterListSupport:
    """Test interpreter evaluation of lists"""

    def test_interpreter_evaluates_empty_list(self):
        """Test evaluating an empty list"""
        interpreter = Interpreter([])
        result = interpreter.evaluate("[]")
        assert result == []

    def test_interpreter_evaluates_list_with_numbers(self):
        """Test evaluating a list with numbers"""
        interpreter = Interpreter([])
        result = interpreter.evaluate("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_interpreter_evaluates_list_with_strings(self):
        """Test evaluating a list with strings"""
        interpreter = Interpreter([])
        result = interpreter.evaluate('["hello", "world"]')
        assert result == ["hello", "world"]

    def test_interpreter_evaluates_list_with_expressions(self):
        """Test evaluating a list with expressions"""
        interpreter = Interpreter([])
        script = "[1 + 2, 3 * 4, 10 - 5]"
        result = interpreter.evaluate(script)
        assert result == [3, 12, 5]

    def test_interpreter_evaluates_list_with_variables(self):
        """Test evaluating a list with variables"""
        interpreter = Interpreter([])
        script = """x = 10
y = 20
z = 30
[x, y, z]"""
        result = interpreter.evaluate(script)
        assert result == [10, 20, 30]

    def test_interpreter_evaluates_nested_lists(self):
        """Test evaluating nested lists"""
        interpreter = Interpreter([])
        result = interpreter.evaluate("[[1, 2], [3, 4], [5, 6]]")
        assert result == [[1, 2], [3, 4], [5, 6]]

    def test_interpreter_list_assignment(self):
        """Test assigning a list to a variable"""
        interpreter = Interpreter([])
        script = """numbers = [1, 2, 3, 4, 5]
numbers"""
        result = interpreter.evaluate(script)
        assert result == [1, 2, 3, 4, 5]

    def test_interpreter_list_as_function_argument(self):
        """Test passing a list as a function argument"""
        def sum_func(numbers: list[float]) -> float:
            """Sum all numbers."""
            return sum(numbers)

        sum_tool = Tool.from_function(sum_func)
        sum_tool.name = "math_operations_sum"

        interpreter = Interpreter([sum_tool])
        script = """from math.operations import sum
result = sum([1, 2, 3, 4, 5])
result"""
        result = interpreter.evaluate(script)
        assert result == 15

    def test_interpreter_multiple_list_arguments(self):
        """Test passing multiple lists as function arguments"""
        def concat_func(list1: list, list2: list) -> list:
            """Concatenate two lists."""
            return list1 + list2

        concat_tool = Tool.from_function(concat_func)
        concat_tool.name = "list_operations_concat"

        interpreter = Interpreter([concat_tool])
        script = """from list.operations import concat
result = concat([1, 2], [3, 4])
result"""
        result = interpreter.evaluate(script)
        assert result == [1, 2, 3, 4]

    def test_interpreter_mixed_arguments(self):
        """Test passing both scalar and list arguments"""
        def prepend_func(item: int, items: list[int]) -> list[int]:
            """Prepend item to list."""
            return [item] + items

        prepend_tool = Tool.from_function(prepend_func)
        prepend_tool.name = "list_operations_prepend"

        interpreter = Interpreter([prepend_tool])
        script = """from list.operations import prepend
result = prepend(0, [1, 2, 3])
result"""
        result = interpreter.evaluate(script)
        assert result == [0, 1, 2, 3]

    def test_interpreter_list_from_variable_in_function_call(self):
        """Test passing a list variable to a function"""
        def length_func(items: list) -> int:
            """Get length of list."""
            return len(items)

        length_tool = Tool.from_function(length_func)
        length_tool.name = "list_operations_length"

        interpreter = Interpreter([length_tool])
        script = """from list.operations import length
numbers = [10, 20, 30, 40]
result = length(numbers)
result"""
        result = interpreter.evaluate(script)
        assert result == 4

    def test_interpreter_list_with_mixed_types(self):
        """Test evaluating a list with mixed types"""
        interpreter = Interpreter([])
        script = """x = 42
[1, "hello", x]"""
        result = interpreter.evaluate(script)
        assert result == [1, "hello", 42]


class TestInterpreterDictSupport:
    """Test interpreter evaluation of dictionaries"""

    def test_interpreter_evaluates_empty_dict(self):
        """Test evaluating an empty dict"""
        interpreter = Interpreter([])
        result = interpreter.evaluate("{}")
        assert result == {}

    def test_interpreter_evaluates_dict_with_string_keys(self):
        """Test evaluating dict with string keys"""
        interpreter = Interpreter([])
        result = interpreter.evaluate('{"name": "John", "age": 30}')
        assert result == {"name": "John", "age": 30}

    def test_interpreter_evaluates_dict_with_variable_keys(self):
        """Test evaluating dict with variable keys"""
        interpreter = Interpreter([])
        script = """x = "name"
y = "age"
{x: "John", y: 30}"""
        result = interpreter.evaluate(script)
        assert result == {"name": "John", "age": 30}

    def test_interpreter_evaluates_dict_with_expression_values(self):
        """Test evaluating dict with expression values"""
        interpreter = Interpreter([])
        script = '{"sum": 1 + 2, "product": 3 * 4}'
        result = interpreter.evaluate(script)
        assert result == {"sum": 3, "product": 12}

    def test_interpreter_evaluates_nested_dicts(self):
        """Test evaluating nested dicts"""
        interpreter = Interpreter([])
        result = interpreter.evaluate('{"outer": {"inner": "value"}}')
        assert result == {"outer": {"inner": "value"}}

    def test_interpreter_dict_assignment(self):
        """Test assigning a dict to a variable"""
        interpreter = Interpreter([])
        script = """person = {"name": "Alice", "age": 25}
person"""
        result = interpreter.evaluate(script)
        assert result == {"name": "Alice", "age": 25}

    def test_interpreter_dict_as_function_argument(self):
        """Test passing a dict as a function argument"""
        def getname(person: dict) -> str:
            """Get name from person dict."""
            return person["name"]

        getname_tool = Tool.from_function(getname)
        getname_tool.name = "data_operations_getname"

        interpreter = Interpreter([getname_tool])
        script = """from data.operations import getname
result = getname({"name": "Bob", "age": 35})
result"""
        result = interpreter.evaluate(script)
        assert result == "Bob"

    def test_interpreter_multiple_dict_arguments(self):
        """Test passing multiple dicts as function arguments"""
        def merge_dicts(dict1: dict, dict2: dict) -> dict:
            """Merge two dicts."""
            result = dict1.copy()
            result.update(dict2)
            return result

        merge_tool = Tool.from_function(merge_dicts)
        merge_tool.name = "data_utils_merge"

        interpreter = Interpreter([merge_tool])
        script = """from data.utils import merge
result = merge({"a": 1}, {"b": 2})
result"""
        result = interpreter.evaluate(script)
        assert result == {"a": 1, "b": 2}

    def test_interpreter_mixed_arguments(self):
        """Test passing both scalar and dict arguments"""
        def addfield(key: str, value: int, data: dict) -> dict:
            """Add field to dict."""
            result = data.copy()
            result[key] = value
            return result

        addfield_tool = Tool.from_function(addfield)
        addfield_tool.name = "data_utils_addfield"

        interpreter = Interpreter([addfield_tool])
        script = """from data.utils import addfield
result = addfield("age", 30, {"name": "Charlie"})
result"""
        result = interpreter.evaluate(script)
        assert result == {"name": "Charlie", "age": 30}

    def test_interpreter_dict_from_variable_in_function_call(self):
        """Test passing a dict variable to a function"""
        def getkeys(data: dict) -> list:
            """Get keys from dict."""
            return list(data.keys())

        getkeys_tool = Tool.from_function(getkeys)
        getkeys_tool.name = "data_utils_getkeys"

        interpreter = Interpreter([getkeys_tool])
        script = """from data.utils import getkeys
config = {"host": "localhost", "port": 8080}
result = getkeys(config)
result"""
        result = interpreter.evaluate(script)
        assert set(result) == {"host", "port"}

    def test_interpreter_dict_with_list_value(self):
        """Test evaluating dict with list as value"""
        interpreter = Interpreter([])
        result = interpreter.evaluate('{"items": [1, 2, 3], "count": 3}')
        assert result == {"items": [1, 2, 3], "count": 3}

    def test_interpreter_dict_with_expression_keys(self):
        """Test evaluating dict with expression keys"""
        interpreter = Interpreter([])
        script = """{1 + 1: "two", 2 + 2: "four"}"""
        result = interpreter.evaluate(script)
        assert result == {2: "two", 4: "four"}

    def test_interpreter_dict_with_number_keys(self):
        """Test evaluating dict with number keys"""
        interpreter = Interpreter([])
        result = interpreter.evaluate('{1: "one", 2: "two", 3: "three"}')
        assert result == {1: "one", 2: "two", 3: "three"}

    def test_interpreter_dict_list_as_key_error(self):
        """Test that using a list as a dict key raises an error"""
        interpreter = Interpreter([])
        script = """{[1, 2]: "value"}"""
        try:
            interpreter.evaluate(script)
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "key" in str(e).lower() or "hashable" in str(e).lower()
