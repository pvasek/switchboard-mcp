import pytest
from src.simple_script import (
    Lexer, Parser, TokenType, Token,
    Number, String, Variable, BinaryOp, Call,
    Assignment, IfStatement, WhileStatement, FunctionDef, Return, ExpressionStatement,
    ImportStatement
)


class TestLexer:
    """Test the lexer/tokenizer"""

    def test_tokenize_numbers(self):
        lexer = Lexer("42 100")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42
        assert tokens[1].type == TokenType.NUMBER
        assert tokens[1].value == 100

    def test_tokenize_strings(self):
        lexer = Lexer('"hello" "world"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"
        assert tokens[1].type == TokenType.STRING
        assert tokens[1].value == "world"

    def test_tokenize_identifiers(self):
        lexer = Lexer("x count my_var")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "x"
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].value == "count"
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].value == "my_var"

    def test_tokenize_keywords(self):
        lexer = Lexer("if else while def return from import")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IF
        assert tokens[1].type == TokenType.ELSE
        assert tokens[2].type == TokenType.WHILE
        assert tokens[3].type == TokenType.DEF
        assert tokens[4].type == TokenType.RETURN
        assert tokens[5].type == TokenType.FROM
        assert tokens[6].type == TokenType.IMPORT

    def test_tokenize_operators(self):
        lexer = Lexer("+ - * / = == < >")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.PLUS
        assert tokens[1].type == TokenType.MINUS
        assert tokens[2].type == TokenType.STAR
        assert tokens[3].type == TokenType.SLASH
        assert tokens[4].type == TokenType.EQUAL
        assert tokens[5].type == TokenType.EQUAL_EQUAL
        assert tokens[6].type == TokenType.LESS
        assert tokens[7].type == TokenType.GREATER

    def test_tokenize_punctuation(self):
        lexer = Lexer("( ) { } ,")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[1].type == TokenType.RPAREN
        assert tokens[2].type == TokenType.LBRACE
        assert tokens[3].type == TokenType.RBRACE
        assert tokens[4].type == TokenType.COMMA

    def test_tokenize_newlines(self):
        lexer = Lexer("x\ny")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[1].type == TokenType.NEWLINE
        assert tokens[2].type == TokenType.IDENTIFIER

    def test_line_tracking(self):
        lexer = Lexer("x\ny\nz")
        tokens = lexer.tokenize()
        assert tokens[0].line == 1
        assert tokens[1].line == 1  # newline
        assert tokens[2].line == 2
        assert tokens[3].line == 2  # newline
        assert tokens[4].line == 3

    def test_tokenize_dot(self):
        lexer = Lexer("mymodule.submodule")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "mymodule"
        assert tokens[1].type == TokenType.DOT
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].value == "submodule"


class TestParserExpressions:
    """Test parsing expressions"""

    def test_parse_number(self):
        lexer = Lexer("42")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert len(ast) == 1
        assert isinstance(ast[0], ExpressionStatement)
        assert isinstance(ast[0].expression, Number)
        assert ast[0].expression.value == 42

    def test_parse_string(self):
        lexer = Lexer('"hello"')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert isinstance(ast[0].expression, String)
        assert ast[0].expression.value == "hello"

    def test_parse_variable(self):
        lexer = Lexer("x")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert isinstance(ast[0].expression, Variable)
        assert ast[0].expression.name == "x"

    def test_parse_binary_addition(self):
        lexer = Lexer("5 + 3")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        expr = ast[0].expression
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "+"
        assert isinstance(expr.left, Number)
        assert expr.left.value == 5
        assert isinstance(expr.right, Number)
        assert expr.right.value == 3

    def test_parse_binary_multiplication(self):
        lexer = Lexer("4 * 2")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        expr = ast[0].expression
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "*"

    def test_parse_comparison(self):
        lexer = Lexer("x == 5")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        expr = ast[0].expression
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "=="

    def test_parse_operator_precedence(self):
        # 2 + 3 * 4 should parse as 2 + (3 * 4)
        lexer = Lexer("2 + 3 * 4")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        expr = ast[0].expression
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "+"
        assert isinstance(expr.left, Number)
        assert expr.left.value == 2
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == "*"

    def test_parse_function_call(self):
        lexer = Lexer("print(42)")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        expr = ast[0].expression
        assert isinstance(expr, Call)
        assert expr.function == "print"
        assert len(expr.arguments) == 1
        assert isinstance(expr.arguments[0], Number)

    def test_parse_function_call_multiple_args(self):
        lexer = Lexer("add(5, 3)")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        expr = ast[0].expression
        assert isinstance(expr, Call)
        assert expr.function == "add"
        assert len(expr.arguments) == 2


class TestParserStatements:
    """Test parsing statements"""

    def test_parse_simple_import(self):
        source = "from mymodule import func1"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert len(ast) == 1
        assert isinstance(ast[0], ImportStatement)
        assert ast[0].module_path == "mymodule"
        assert ast[0].names == ["func1"]

    def test_parse_dotted_import(self):
        source = "from mymodule.submodule import func1"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        stmt = ast[0]
        assert isinstance(stmt, ImportStatement)
        assert stmt.module_path == "mymodule.submodule"
        assert stmt.names == ["func1"]

    def test_parse_multiple_imports(self):
        source = "from mymodule import func1, func2"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        stmt = ast[0]
        assert isinstance(stmt, ImportStatement)
        assert stmt.module_path == "mymodule"
        assert stmt.names == ["func1", "func2"]

    def test_parse_dotted_multiple_imports(self):
        source = "from math.utils import add, subtract, multiply"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        stmt = ast[0]
        assert isinstance(stmt, ImportStatement)
        assert stmt.module_path == "math.utils"
        assert stmt.names == ["add", "subtract", "multiply"]

    def test_parse_assignment(self):
        lexer = Lexer("x = 42")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert len(ast) == 1
        assert isinstance(ast[0], Assignment)
        assert ast[0].name == "x"
        assert isinstance(ast[0].value, Number)
        assert ast[0].value.value == 42

    def test_parse_assignment_expression(self):
        lexer = Lexer("result = 5 + 3")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        stmt = ast[0]
        assert isinstance(stmt, Assignment)
        assert stmt.name == "result"
        assert isinstance(stmt.value, BinaryOp)

    def test_parse_if_statement(self):
        source = """if x > 5:
    y = 10"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert len(ast) == 1
        assert isinstance(ast[0], IfStatement)
        assert isinstance(ast[0].condition, BinaryOp)
        assert len(ast[0].then_block) == 1
        assert len(ast[0].else_block) == 0

    def test_parse_if_else_statement(self):
        source = """if x > 0:
    y = 1
else:
    y = 0"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        stmt = ast[0]
        assert isinstance(stmt, IfStatement)
        assert len(stmt.then_block) == 1
        assert len(stmt.else_block) == 1

    def test_parse_while_statement(self):
        source = """while count < 10:
    count = count + 1"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert len(ast) == 1
        assert isinstance(ast[0], WhileStatement)
        assert isinstance(ast[0].condition, BinaryOp)
        assert len(ast[0].body) == 1

    def test_parse_function_def(self):
        source = """def add(a, b):
    return a + b"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert len(ast) == 1
        assert isinstance(ast[0], FunctionDef)
        assert ast[0].name == "add"
        assert ast[0].parameters == ["a", "b"]
        assert len(ast[0].body) == 1
        assert isinstance(ast[0].body[0], Return)

    def test_parse_function_def_no_params(self):
        source = """def hello():
    print("hello")"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        func = ast[0]
        assert isinstance(func, FunctionDef)
        assert func.name == "hello"
        assert func.parameters == []

    def test_parse_return_statement(self):
        source = """def get_five():
    return 5"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        func = ast[0]
        assert isinstance(func.body[0], Return)
        assert isinstance(func.body[0].value, Number)


class TestIntegration:
    """Test complete programs"""

    def test_factorial_program(self):
        source = """def factorial(n):
    result = 1
    counter = 1
    while counter < n:
        counter = counter + 1
        result = result * counter
    return result

num = 5
fact = factorial(num)"""

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # Should have 3 top-level statements
        assert len(ast) == 3
        assert isinstance(ast[0], FunctionDef)
        assert isinstance(ast[1], Assignment)
        assert isinstance(ast[2], Assignment)

        # Check function structure
        func = ast[0]
        assert func.name == "factorial"
        assert func.parameters == ["n"]
        assert len(func.body) == 4  # 2 assignments, 1 while, 1 return

    def test_conditional_program(self):
        source = """x = 10
if x > 5:
    print("greater")
else:
    print("lesser")"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 2
        assert isinstance(ast[0], Assignment)
        assert isinstance(ast[1], IfStatement)

    def test_multiple_statements(self):
        source = """x = 5
y = 10
z = x + y
print(z)"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 4
        assert all(isinstance(stmt, (Assignment, ExpressionStatement)) for stmt in ast)

    def test_nested_expressions(self):
        source = "result = (x + y) * (a - b)"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        stmt = ast[0]
        assert isinstance(stmt, Assignment)
        assert isinstance(stmt.value, BinaryOp)
        assert stmt.value.operator == "*"

    def test_error_unexpected_character(self):
        with pytest.raises(SyntaxError, match="Unexpected character"):
            lexer = Lexer("x = 5 @ 3")
            lexer.tokenize()

    def test_error_unexpected_token(self):
        with pytest.raises(SyntaxError):
            lexer = Lexer("+ + +")
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            parser.parse()

    def test_program_with_imports(self):
        source = """from math.utils import factorial
from io.display import print_result

num = 5
fact = factorial(num)
print_result(fact)"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # Should have 5 top-level statements: 2 imports + 3 statements
        assert len(ast) == 5
        assert isinstance(ast[0], ImportStatement)
        assert isinstance(ast[1], ImportStatement)
        assert isinstance(ast[2], Assignment)
        assert isinstance(ast[3], Assignment)
        assert isinstance(ast[4], ExpressionStatement)

        # Check first import
        assert ast[0].module_path == "math.utils"
        assert ast[0].names == ["factorial"]

        # Check second import
        assert ast[1].module_path == "io.display"
        assert ast[1].names == ["print_result"]

    def test_import_module_alias_simple(self):
        """Test simple module alias import: import math as m"""
        source = """import math as m"""

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        assert isinstance(ast[0], ImportStatement)
        assert ast[0].module_path == "math"
        assert ast[0].alias == "m"
        assert ast[0].names is None

    def test_import_module_alias_dotted(self):
        """Test dotted module alias import: import math.operations as ops"""
        source = """import math.operations as ops"""

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        assert isinstance(ast[0], ImportStatement)
        assert ast[0].module_path == "math.operations"
        assert ast[0].alias == "ops"
        assert ast[0].names is None

    def test_import_module_alias_deeply_nested(self):
        """Test deeply nested module alias: import module.sub.subsub as alias"""
        source = """import module.sub.subsub as alias"""

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        assert isinstance(ast[0], ImportStatement)
        assert ast[0].module_path == "module.sub.subsub"
        assert ast[0].alias == "alias"
        assert ast[0].names is None

    def test_mixed_import_styles(self):
        """Test mixing selective imports and module aliases"""
        source = """from math.statistics import min, max
import math.operations as ops
from io import print_result
import math.random as rand"""

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 4

        # First: selective import
        assert isinstance(ast[0], ImportStatement)
        assert ast[0].module_path == "math.statistics"
        assert ast[0].names == ["min", "max"]
        assert ast[0].alias is None

        # Second: module alias
        assert isinstance(ast[1], ImportStatement)
        assert ast[1].module_path == "math.operations"
        assert ast[1].alias == "ops"
        assert ast[1].names is None

        # Third: selective import
        assert isinstance(ast[2], ImportStatement)
        assert ast[2].module_path == "io"
        assert ast[2].names == ["print_result"]
        assert ast[2].alias is None

        # Fourth: module alias
        assert isinstance(ast[3], ImportStatement)
        assert ast[3].module_path == "math.random"
        assert ast[3].alias == "rand"
        assert ast[3].names is None

    def test_dotted_function_call_parsing(self):
        """Test parsing dotted function calls like ops.plus(1, 2)"""
        source = """result = ops.plus(1, 2)"""

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 1
        assert isinstance(ast[0], Assignment)
        assert ast[0].name == "result"

        # Check the call expression
        call_expr = ast[0].value
        assert isinstance(call_expr, Call)
        assert call_expr.function == "ops.plus"
        assert len(call_expr.arguments) == 2
        assert isinstance(call_expr.arguments[0], Number)
        assert call_expr.arguments[0].value == 1
        assert isinstance(call_expr.arguments[1], Number)
        assert call_expr.arguments[1].value == 2

    def test_multiple_dotted_function_calls(self):
        """Test multiple dotted function calls in a program"""
        source = """import math.operations as ops
x = ops.plus(5, 3)
y = ops.multiply(x, 2)
z = ops.minus(y, 1)"""

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        assert len(ast) == 4
        assert isinstance(ast[0], ImportStatement)
        assert ast[0].module_path == "math.operations"
        assert ast[0].alias == "ops"

        # Check each assignment
        for i in range(1, 4):
            assert isinstance(ast[i], Assignment)
            assert isinstance(ast[i].value, Call)
            assert ast[i].value.function.startswith("ops.")

        assert ast[1].value.function == "ops.plus"
        assert ast[2].value.function == "ops.multiply"
        assert ast[3].value.function == "ops.minus"
