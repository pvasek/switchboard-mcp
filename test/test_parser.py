import pytest
from src.simple_script.lexer import Lexer
from src.simple_script.parser import (
    Parser,
    ListLiteral,
    Number,
    String,
    Variable,
    Assignment,
    Call,
    BinaryOp,
    ExpressionStatement,
)


class TestParserListSupport:
    """Test parser parsing of list literals"""

    def test_parse_empty_list(self):
        """Test parsing an empty list []"""
        lexer = Lexer("[]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        assert isinstance(ast[0], ExpressionStatement)
        assert isinstance(ast[0].expression, ListLiteral)
        assert len(ast[0].expression.elements) == 0

    def test_parse_list_with_numbers(self):
        """Test parsing a list with numbers [1, 2, 3]"""
        lexer = Lexer("[1, 2, 3]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        assert isinstance(ast[0], ExpressionStatement)
        list_literal = ast[0].expression
        assert isinstance(list_literal, ListLiteral)
        assert len(list_literal.elements) == 3
        assert all(isinstance(elem, Number) for elem in list_literal.elements)
        assert list_literal.elements[0].value == 1
        assert list_literal.elements[1].value == 2
        assert list_literal.elements[2].value == 3

    def test_parse_list_with_strings(self):
        """Test parsing a list with strings ["hello", "world"]"""
        lexer = Lexer('["hello", "world"]')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        list_literal = ast[0].expression
        assert isinstance(list_literal, ListLiteral)
        assert len(list_literal.elements) == 2
        assert all(isinstance(elem, String) for elem in list_literal.elements)
        assert list_literal.elements[0].value == "hello"
        assert list_literal.elements[1].value == "world"

    def test_parse_list_with_variables(self):
        """Test parsing a list with variables [x, y, z]"""
        lexer = Lexer("[x, y, z]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        list_literal = ast[0].expression
        assert isinstance(list_literal, ListLiteral)
        assert len(list_literal.elements) == 3
        assert all(isinstance(elem, Variable) for elem in list_literal.elements)
        assert list_literal.elements[0].name == "x"
        assert list_literal.elements[1].name == "y"
        assert list_literal.elements[2].name == "z"

    def test_parse_list_with_expressions(self):
        """Test parsing a list with expressions [1 + 2, 3 * 4]"""
        lexer = Lexer("[1 + 2, 3 * 4]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        list_literal = ast[0].expression
        assert isinstance(list_literal, ListLiteral)
        assert len(list_literal.elements) == 2
        assert all(isinstance(elem, BinaryOp) for elem in list_literal.elements)
        assert list_literal.elements[0].operator == "+"
        assert list_literal.elements[1].operator == "*"

    def test_parse_nested_lists(self):
        """Test parsing nested lists [[1, 2], [3, 4]]"""
        lexer = Lexer("[[1, 2], [3, 4]]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        outer_list = ast[0].expression
        assert isinstance(outer_list, ListLiteral)
        assert len(outer_list.elements) == 2

        # Check first nested list
        inner_list1 = outer_list.elements[0]
        assert isinstance(inner_list1, ListLiteral)
        assert len(inner_list1.elements) == 2
        assert inner_list1.elements[0].value == 1
        assert inner_list1.elements[1].value == 2

        # Check second nested list
        inner_list2 = outer_list.elements[1]
        assert isinstance(inner_list2, ListLiteral)
        assert len(inner_list2.elements) == 2
        assert inner_list2.elements[0].value == 3
        assert inner_list2.elements[1].value == 4

    def test_parse_list_assignment(self):
        """Test parsing list assignment: numbers = [1, 2, 3]"""
        lexer = Lexer("numbers = [1, 2, 3]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        assert isinstance(ast[0], Assignment)
        assert ast[0].name == "numbers"
        assert isinstance(ast[0].value, ListLiteral)
        assert len(ast[0].value.elements) == 3

    def test_parse_list_as_function_argument(self):
        """Test parsing list as function argument: min([1, 2, 3])"""
        lexer = Lexer("min([1, 2, 3])")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        assert isinstance(ast[0], ExpressionStatement)
        call = ast[0].expression
        assert isinstance(call, Call)
        assert call.function == "min"
        assert len(call.arguments) == 1
        assert isinstance(call.arguments[0], ListLiteral)
        assert len(call.arguments[0].elements) == 3

    def test_parse_multiple_list_arguments(self):
        """Test parsing multiple list arguments: func([1, 2], [3, 4])"""
        lexer = Lexer("func([1, 2], [3, 4])")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        call = ast[0].expression
        assert isinstance(call, Call)
        assert call.function == "func"
        assert len(call.arguments) == 2
        assert isinstance(call.arguments[0], ListLiteral)
        assert isinstance(call.arguments[1], ListLiteral)
        assert len(call.arguments[0].elements) == 2
        assert len(call.arguments[1].elements) == 2

    def test_parse_list_with_mixed_types(self):
        """Test parsing list with mixed types [1, "hello", x]"""
        lexer = Lexer('[1, "hello", x]')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        list_literal = ast[0].expression
        assert isinstance(list_literal, ListLiteral)
        assert len(list_literal.elements) == 3
        assert isinstance(list_literal.elements[0], Number)
        assert isinstance(list_literal.elements[1], String)
        assert isinstance(list_literal.elements[2], Variable)

    def test_parse_variable_and_list_as_arguments(self):
        """Test parsing variable and list as separate arguments: func(x, [1, 2])"""
        lexer = Lexer("func(x, [1, 2])")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        call = ast[0].expression
        assert isinstance(call, Call)
        assert len(call.arguments) == 2
        assert isinstance(call.arguments[0], Variable)
        assert isinstance(call.arguments[1], ListLiteral)

    def test_parse_list_in_assignment_with_variable(self):
        """Test parsing list in assignment with variable: result = process([x, y, z])"""
        lexer = Lexer("result = process([x, y, z])")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        assert isinstance(ast[0], Assignment)
        assert ast[0].name == "result"
        assert isinstance(ast[0].value, Call)
        assert ast[0].value.function == "process"
        assert len(ast[0].value.arguments) == 1
        assert isinstance(ast[0].value.arguments[0], ListLiteral)


class TestParserDictSupport:
    """Test parser parsing of dictionary literals"""

    def test_parse_empty_dict(self):
        """Test parsing an empty dict {}"""
        from src.simple_script.parser import DictLiteral

        lexer = Lexer("{}")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        assert isinstance(ast[0], ExpressionStatement)
        assert isinstance(ast[0].expression, DictLiteral)
        assert len(ast[0].expression.pairs) == 0

    def test_parse_dict_with_string_keys(self):
        """Test parsing dict with string keys {"a": 1, "b": 2}"""
        from src.simple_script.parser import DictLiteral

        lexer = Lexer('{"a": 1, "b": 2}')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        dict_literal = ast[0].expression
        assert isinstance(dict_literal, DictLiteral)
        assert len(dict_literal.pairs) == 2

        # Check first pair
        key1, val1 = dict_literal.pairs[0]
        assert isinstance(key1, String)
        assert key1.value == "a"
        assert isinstance(val1, Number)
        assert val1.value == 1

        # Check second pair
        key2, val2 = dict_literal.pairs[1]
        assert isinstance(key2, String)
        assert key2.value == "b"
        assert isinstance(val2, Number)
        assert val2.value == 2

    def test_parse_dict_with_variable_keys(self):
        """Test parsing dict with variable keys {x: 1, y: 2}"""
        from src.simple_script.parser import DictLiteral

        lexer = Lexer("{x: 1, y: 2}")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        dict_literal = ast[0].expression
        assert isinstance(dict_literal, DictLiteral)
        assert len(dict_literal.pairs) == 2

        # Check variable keys
        key1, val1 = dict_literal.pairs[0]
        assert isinstance(key1, Variable)
        assert key1.name == "x"

        key2, val2 = dict_literal.pairs[1]
        assert isinstance(key2, Variable)
        assert key2.name == "y"

    def test_parse_dict_with_expression_values(self):
        """Test parsing dict with expression values {x: 1 + 2, y: 3 * 4}"""
        from src.simple_script.parser import DictLiteral

        lexer = Lexer("{x: 1 + 2, y: 3 * 4}")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        dict_literal = ast[0].expression
        assert isinstance(dict_literal, DictLiteral)
        assert len(dict_literal.pairs) == 2

        # Check expression values
        key1, val1 = dict_literal.pairs[0]
        assert isinstance(val1, BinaryOp)
        assert val1.operator == "+"

        key2, val2 = dict_literal.pairs[1]
        assert isinstance(val2, BinaryOp)
        assert val2.operator == "*"

    def test_parse_nested_dicts(self):
        """Test parsing nested dicts {"outer": {"inner": 1}}"""
        from src.simple_script.parser import DictLiteral

        lexer = Lexer('{"outer": {"inner": 1}}')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        outer_dict = ast[0].expression
        assert isinstance(outer_dict, DictLiteral)
        assert len(outer_dict.pairs) == 1

        # Check outer dict
        key, val = outer_dict.pairs[0]
        assert isinstance(key, String)
        assert key.value == "outer"

        # Check inner dict
        assert isinstance(val, DictLiteral)
        assert len(val.pairs) == 1
        inner_key, inner_val = val.pairs[0]
        assert isinstance(inner_key, String)
        assert inner_key.value == "inner"
        assert isinstance(inner_val, Number)
        assert inner_val.value == 1

    def test_parse_dict_assignment(self):
        """Test parsing dict assignment: person = {"name": "John"}"""
        from src.simple_script.parser import DictLiteral

        lexer = Lexer('person = {"name": "John"}')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        assert isinstance(ast[0], Assignment)
        assert ast[0].name == "person"
        assert isinstance(ast[0].value, DictLiteral)
        assert len(ast[0].value.pairs) == 1

    def test_parse_dict_as_function_argument(self):
        """Test parsing dict as function argument: func({"key": "value"})"""
        from src.simple_script.parser import DictLiteral

        lexer = Lexer('func({"key": "value"})')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        call = ast[0].expression
        assert isinstance(call, Call)
        assert call.function == "func"
        assert len(call.arguments) == 1
        assert isinstance(call.arguments[0], DictLiteral)

    def test_parse_multiple_dict_arguments(self):
        """Test parsing multiple dict arguments: func({"a": 1}, {"b": 2})"""
        from src.simple_script.parser import DictLiteral

        lexer = Lexer('func({"a": 1}, {"b": 2})')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        call = ast[0].expression
        assert isinstance(call, Call)
        assert len(call.arguments) == 2
        assert isinstance(call.arguments[0], DictLiteral)
        assert isinstance(call.arguments[1], DictLiteral)

    def test_parse_mixed_arguments(self):
        """Test parsing mixed scalar and dict arguments: func(x, {"key": 1})"""
        from src.simple_script.parser import DictLiteral

        lexer = Lexer('func(x, {"key": 1})')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        call = ast[0].expression
        assert isinstance(call, Call)
        assert len(call.arguments) == 2
        assert isinstance(call.arguments[0], Variable)
        assert isinstance(call.arguments[1], DictLiteral)

    def test_parse_dict_with_mixed_types(self):
        """Test parsing dict with mixed types {"a": 1, "b": "text", "c": x}"""
        from src.simple_script.parser import DictLiteral

        lexer = Lexer('{"a": 1, "b": "text", "c": x}')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        dict_literal = ast[0].expression
        assert isinstance(dict_literal, DictLiteral)
        assert len(dict_literal.pairs) == 3

        # Check types
        _, val1 = dict_literal.pairs[0]
        assert isinstance(val1, Number)

        _, val2 = dict_literal.pairs[1]
        assert isinstance(val2, String)

        _, val3 = dict_literal.pairs[2]
        assert isinstance(val3, Variable)

    def test_parse_dict_with_list_value(self):
        """Test parsing dict with list as value: {"items": [1, 2, 3]}"""
        from src.simple_script.parser import DictLiteral

        lexer = Lexer('{"items": [1, 2, 3]}')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        dict_literal = ast[0].expression
        assert isinstance(dict_literal, DictLiteral)
        assert len(dict_literal.pairs) == 1

        key, val = dict_literal.pairs[0]
        assert isinstance(key, String)
        assert isinstance(val, ListLiteral)
        assert len(val.elements) == 3
