import pytest
from simple_script.lexer import Lexer, TokenType


class TestLexerListSupport:
    """Test lexer tokenization of list literals"""

    def test_tokenize_empty_list(self):
        """Test tokenizing an empty list []"""
        lexer = Lexer("[]")
        tokens = lexer.tokenize()

        assert len(tokens) == 3  # LBRACKET, RBRACKET, EOF
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].type == TokenType.RBRACKET
        assert tokens[2].type == TokenType.EOF

    def test_tokenize_list_with_numbers(self):
        """Test tokenizing a list with numbers [1, 2, 3]"""
        lexer = Lexer("[1, 2, 3]")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.RBRACKET,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type, f"Token {i} mismatch"

    def test_tokenize_list_with_strings(self):
        """Test tokenizing a list with strings ["hello", "world"]"""
        lexer = Lexer('["hello", "world"]')
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACKET,
            TokenType.STRING,
            TokenType.COMMA,
            TokenType.STRING,
            TokenType.RBRACKET,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        assert tokens[1].value == "hello"
        assert tokens[3].value == "world"

    def test_tokenize_list_with_variables(self):
        """Test tokenizing a list with variables [x, y, z]"""
        lexer = Lexer("[x, y, z]")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACKET,
            TokenType.IDENTIFIER,
            TokenType.COMMA,
            TokenType.IDENTIFIER,
            TokenType.COMMA,
            TokenType.IDENTIFIER,
            TokenType.RBRACKET,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        assert tokens[1].value == "x"
        assert tokens[3].value == "y"
        assert tokens[5].value == "z"

    def test_tokenize_list_with_expressions(self):
        """Test tokenizing a list with expressions [1 + 2, 3 * 4]"""
        lexer = Lexer("[1 + 2, 3 * 4]")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.PLUS,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.STAR,
            TokenType.NUMBER,
            TokenType.RBRACKET,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)

    def test_tokenize_nested_lists(self):
        """Test tokenizing nested lists [[1, 2], [3, 4]]"""
        lexer = Lexer("[[1, 2], [3, 4]]")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACKET,
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.RBRACKET,
            TokenType.COMMA,
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.RBRACKET,
            TokenType.RBRACKET,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type

    def test_tokenize_list_assignment(self):
        """Test tokenizing list assignment: numbers = [1, 2, 3]"""
        lexer = Lexer("numbers = [1, 2, 3]")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IDENTIFIER,
            TokenType.EQUAL,
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.RBRACKET,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        assert tokens[0].value == "numbers"

    def test_tokenize_list_as_function_argument(self):
        """Test tokenizing list as function argument: min([1, 2, 3])"""
        lexer = Lexer("min([1, 2, 3])")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.RBRACKET,
            TokenType.RPAREN,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        assert tokens[0].value == "min"

    def test_tokenize_multiple_list_arguments(self):
        """Test tokenizing multiple list arguments: func([1, 2], [3, 4])"""
        lexer = Lexer("func([1, 2], [3, 4])")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.RBRACKET,
            TokenType.COMMA,
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.NUMBER,
            TokenType.RBRACKET,
            TokenType.RPAREN,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)

    def test_tokenize_list_with_mixed_types(self):
        """Test tokenizing list with mixed types [1, "hello", x]"""
        lexer = Lexer('[1, "hello", x]')
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.STRING,
            TokenType.COMMA,
            TokenType.IDENTIFIER,
            TokenType.RBRACKET,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        assert tokens[1].value == 1
        assert tokens[3].value == "hello"
        assert tokens[5].value == "x"


class TestLexerDictSupport:
    """Test lexer tokenization of dictionary literals"""

    def test_tokenize_empty_dict(self):
        """Test tokenizing an empty dict {}"""
        lexer = Lexer("{}")
        tokens = lexer.tokenize()

        assert len(tokens) == 3  # LBRACE, RBRACE, EOF
        assert tokens[0].type == TokenType.LBRACE
        assert tokens[1].type == TokenType.RBRACE
        assert tokens[2].type == TokenType.EOF

    def test_tokenize_dict_with_string_keys(self):
        """Test tokenizing dict with string keys {"a": 1, "b": 2}"""
        lexer = Lexer('{"a": 1, "b": 2}')
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACE,
            TokenType.STRING,      # "a"
            TokenType.COLON,
            TokenType.NUMBER,      # 1
            TokenType.COMMA,
            TokenType.STRING,      # "b"
            TokenType.COLON,
            TokenType.NUMBER,      # 2
            TokenType.RBRACE,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type, f"Token {i} mismatch"

    def test_tokenize_dict_with_variable_keys(self):
        """Test tokenizing dict with variable keys {x: 1, y: 2}"""
        lexer = Lexer("{x: 1, y: 2}")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACE,
            TokenType.IDENTIFIER,  # x
            TokenType.COLON,
            TokenType.NUMBER,      # 1
            TokenType.COMMA,
            TokenType.IDENTIFIER,  # y
            TokenType.COLON,
            TokenType.NUMBER,      # 2
            TokenType.RBRACE,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        assert tokens[1].value == "x"
        assert tokens[5].value == "y"

    def test_tokenize_dict_with_string_values(self):
        """Test tokenizing dict with string values {"name": "Alice"}"""
        lexer = Lexer('{"name": "Alice", "city": "NYC"}')
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACE,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.STRING,
            TokenType.COMMA,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.STRING,
            TokenType.RBRACE,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        assert tokens[1].value == "name"
        assert tokens[3].value == "Alice"

    def test_tokenize_nested_dicts(self):
        """Test tokenizing nested dicts {"outer": {"inner": "value"}}"""
        lexer = Lexer('{"outer": {"inner": "value"}}')
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACE,
            TokenType.STRING,      # "outer"
            TokenType.COLON,
            TokenType.LBRACE,      # nested dict start
            TokenType.STRING,      # "inner"
            TokenType.COLON,
            TokenType.STRING,      # "value"
            TokenType.RBRACE,      # nested dict end
            TokenType.RBRACE,      # outer dict end
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type

    def test_tokenize_dict_assignment(self):
        """Test tokenizing dict assignment: person = {"name": "John"}"""
        lexer = Lexer('person = {"name": "John"}')
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IDENTIFIER,  # person
            TokenType.EQUAL,
            TokenType.LBRACE,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.STRING,
            TokenType.RBRACE,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        assert tokens[0].value == "person"

    def test_tokenize_dict_as_function_argument(self):
        """Test tokenizing dict as function argument: func({"key": "value"})"""
        lexer = Lexer('func({"key": "value"})')
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LBRACE,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.STRING,
            TokenType.RBRACE,
            TokenType.RPAREN,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        assert tokens[0].value == "func"

    def test_tokenize_multiple_dict_arguments(self):
        """Test tokenizing multiple dict arguments: func({"a": 1}, {"b": 2})"""
        lexer = Lexer('func({"a": 1}, {"b": 2})')
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.LBRACE,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.NUMBER,
            TokenType.RBRACE,
            TokenType.COMMA,
            TokenType.LBRACE,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.NUMBER,
            TokenType.RBRACE,
            TokenType.RPAREN,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)

    def test_tokenize_dict_with_expressions(self):
        """Test tokenizing dict with expression values: {x: 1 + 2}"""
        lexer = Lexer("{x: 1 + 2, y: 3 * 4}")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACE,
            TokenType.IDENTIFIER,  # x
            TokenType.COLON,
            TokenType.NUMBER,      # 1
            TokenType.PLUS,
            TokenType.NUMBER,      # 2
            TokenType.COMMA,
            TokenType.IDENTIFIER,  # y
            TokenType.COLON,
            TokenType.NUMBER,      # 3
            TokenType.STAR,
            TokenType.NUMBER,      # 4
            TokenType.RBRACE,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)

    def test_tokenize_dict_with_mixed_types(self):
        """Test tokenizing dict with mixed key and value types"""
        lexer = Lexer('{"a": 1, "b": "text", "c": x}')
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.LBRACE,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.STRING,
            TokenType.COMMA,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.IDENTIFIER,
            TokenType.RBRACE,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)


class TestLexerMultilineStringSupport:
    """Test lexer tokenization of multiline strings"""

    def test_tokenize_double_quote_multiline_string(self):
        """Test tokenizing triple double-quoted multiline string"""
        source = '''"""This is a
multiline string
with multiple lines"""'''
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        assert len(tokens) == 2  # STRING, EOF
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == """This is a
multiline string
with multiple lines"""
        assert tokens[1].type == TokenType.EOF

    def test_tokenize_single_quote_multiline_string(self):
        """Test tokenizing triple single-quoted multiline string"""
        source = """'''This is also
a multiline string
using single quotes'''"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        assert len(tokens) == 2  # STRING, EOF
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == """This is also
a multiline string
using single quotes"""
        assert tokens[1].type == TokenType.EOF

    def test_tokenize_multiline_string_with_indentation(self):
        """Test that multiline strings preserve indentation"""
        source = '''"""Line 1
    Line 2 indented
Line 3"""'''
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        assert len(tokens) == 2
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == """Line 1
    Line 2 indented
Line 3"""

    def test_tokenize_multiline_string_assignment(self):
        """Test tokenizing assignment with multiline string"""
        source = '''text = """First line
Second line
Third line"""'''
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IDENTIFIER,
            TokenType.EQUAL,
            TokenType.STRING,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type, f"Token {i} mismatch"

        assert tokens[0].value == "text"
        assert tokens[2].value == """First line
Second line
Third line"""

    def test_tokenize_multiline_string_as_function_argument(self):
        """Test tokenizing function call with multiline string argument"""
        source = '''print("""Hello
World""")'''
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IDENTIFIER,
            TokenType.LPAREN,
            TokenType.STRING,
            TokenType.RPAREN,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        assert tokens[0].value == "print"
        assert tokens[2].value == """Hello
World"""

    def test_tokenize_empty_multiline_string(self):
        """Test tokenizing empty multiline string"""
        lexer = Lexer('""""""')
        tokens = lexer.tokenize()

        assert len(tokens) == 2
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == ""
        assert tokens[1].type == TokenType.EOF

    def test_tokenize_multiline_string_with_quotes_inside(self):
        """Test multiline string containing single quotes"""
        source = '''"""It's a "nice" day"""'''
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        assert len(tokens) == 2
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == '''It's a "nice" day'''

    def test_tokenize_multiple_multiline_strings(self):
        """Test tokenizing multiple multiline strings in sequence"""
        source = """first = \"\"\"Line 1
Line 2\"\"\"
second = '''Line 3
Line 4'''"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        # first, =, STRING, NEWLINE, second, =, STRING, EOF
        assert tokens[0].value == "first"
        assert tokens[1].type == TokenType.EQUAL
        assert tokens[2].type == TokenType.STRING
        assert tokens[2].value == """Line 1
Line 2"""
        assert tokens[3].type == TokenType.NEWLINE
        assert tokens[4].value == "second"
        assert tokens[5].type == TokenType.EQUAL
        assert tokens[6].type == TokenType.STRING
        assert tokens[6].value == """Line 3
Line 4"""

    def test_distinguish_single_vs_triple_quotes(self):
        """Test that single quotes don't interfere with triple quotes"""
        # Single quotes should work normally
        lexer1 = Lexer('"hello"')
        tokens1 = lexer1.tokenize()
        assert tokens1[0].value == "hello"

        # Triple quotes should also work
        lexer2 = Lexer('"""hello"""')
        tokens2 = lexer2.tokenize()
        assert tokens2[0].value == "hello"


class TestLexerImportAliasSupport:
    """Test lexer tokenization of import alias statements"""

    def test_tokenize_import_as_keyword(self):
        """Test tokenizing 'as' keyword"""
        lexer = Lexer("as")
        tokens = lexer.tokenize()

        assert len(tokens) == 2  # AS, EOF
        assert tokens[0].type == TokenType.AS
        assert tokens[1].type == TokenType.EOF

    def test_tokenize_simple_import_alias(self):
        """Test tokenizing 'import module as m'"""
        lexer = Lexer("import module as m")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IMPORT,
            TokenType.IDENTIFIER,
            TokenType.AS,
            TokenType.IDENTIFIER,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type, f"Token {i} mismatch"

        assert tokens[1].value == "module"
        assert tokens[3].value == "m"

    def test_tokenize_dotted_import_alias(self):
        """Test tokenizing 'import math.operations as ops'"""
        lexer = Lexer("import math.operations as ops")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IMPORT,
            TokenType.IDENTIFIER,
            TokenType.DOT,
            TokenType.IDENTIFIER,
            TokenType.AS,
            TokenType.IDENTIFIER,
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type, f"Token {i} mismatch"

        assert tokens[1].value == "math"
        assert tokens[3].value == "operations"
        assert tokens[5].value == "ops"

    def test_tokenize_deeply_nested_import_alias(self):
        """Test tokenizing 'import module.sub.subsub as alias'"""
        lexer = Lexer("import module.sub.subsub as alias")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.IMPORT,
            TokenType.IDENTIFIER,  # module
            TokenType.DOT,
            TokenType.IDENTIFIER,  # sub
            TokenType.DOT,
            TokenType.IDENTIFIER,  # subsub
            TokenType.AS,
            TokenType.IDENTIFIER,  # alias
            TokenType.EOF,
        ]

        assert len(tokens) == len(expected_types)
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type, f"Token {i} mismatch"

        assert tokens[1].value == "module"
        assert tokens[3].value == "sub"
        assert tokens[5].value == "subsub"
        assert tokens[7].value == "alias"
