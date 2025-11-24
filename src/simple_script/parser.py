from dataclasses import dataclass

from src.simple_script.lexer import TokenType


@dataclass
class ASTNode:
    pass


# Expressions
@dataclass
class Number(ASTNode):
    value: int


@dataclass
class String(ASTNode):
    value: str


@dataclass
class Variable(ASTNode):
    name: str


@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class Call(ASTNode):
    function: str
    arguments: list[ASTNode]


@dataclass
class ListLiteral(ASTNode):
    elements: list[ASTNode]


@dataclass
class DictLiteral(ASTNode):
    pairs: list[tuple[ASTNode, ASTNode]]


# Statements
@dataclass
class ImportStatement(ASTNode):
    module_path: str
    names: list[str] | None = None  # For selective imports: from X import a, b
    alias: str | None = None  # For module aliases: import X as Y


@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode


@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_block: list[ASTNode]
    else_block: list[ASTNode]


@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: list[ASTNode]


@dataclass
class FunctionDef(ASTNode):
    name: str
    parameters: list[str]
    body: list[ASTNode]


@dataclass
class Return(ASTNode):
    value: ASTNode


@dataclass
class ExpressionStatement(ASTNode):
    expression: ASTNode


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]

    def advance(self):
        self.pos += 1

    def expect(self, token_type):
        if self.current_token().type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token().type}")
        token = self.current_token()
        self.advance()
        return token

    def skip_newlines(self):
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()

    def parse(self):
        statements = []
        self.skip_newlines()

        while self.current_token().type != TokenType.EOF:
            statements.append(self.parse_statement())
            self.skip_newlines()

        return statements

    def parse_statement(self):
        self.skip_newlines()

        # Import statement (both styles)
        if self.current_token().type in (TokenType.FROM, TokenType.IMPORT):
            return self.parse_import_statement()

        # Function definition
        if self.current_token().type == TokenType.DEF:
            return self.parse_function_def()

        # If statement
        if self.current_token().type == TokenType.IF:
            return self.parse_if_statement()

        # While statement
        if self.current_token().type == TokenType.WHILE:
            return self.parse_while_statement()

        # Return statement
        if self.current_token().type == TokenType.RETURN:
            self.advance()
            value = self.parse_expression()
            self.skip_newlines()
            return Return(value)

        # Assignment or expression
        if self.current_token().type == TokenType.IDENTIFIER:
            name = self.current_token().value
            self.advance()

            if self.current_token().type == TokenType.EQUAL:
                self.advance()
                value = self.parse_expression()
                self.skip_newlines()
                return Assignment(name, value)
            else:
                # It's a function call
                self.pos -= 1  # backtrack
                expr = self.parse_expression()
                self.skip_newlines()
                return ExpressionStatement(expr)

        # Just an expression
        expr = self.parse_expression()
        self.skip_newlines()
        return ExpressionStatement(expr)

    def parse_import_statement(self):
        """Parse import statements.

        Two styles supported:
        1. from module.path import name1, name2
        2. import module.path as alias
        """
        current = self.current_token()

        if current.type == TokenType.FROM:
            # Selective import: from module import name1, name2
            self.expect(TokenType.FROM)

            # Parse module path (e.g., mymodule.submodule)
            module_parts = []
            module_parts.append(self.expect(TokenType.IDENTIFIER).value)
            while self.current_token().type == TokenType.DOT:
                self.advance()  # skip dot
                module_parts.append(self.expect(TokenType.IDENTIFIER).value)
            module_path = ".".join(module_parts)

            self.expect(TokenType.IMPORT)

            # Parse import names
            names = []
            names.append(self.expect(TokenType.IDENTIFIER).value)
            while self.current_token().type == TokenType.COMMA:
                self.advance()  # skip comma
                names.append(self.expect(TokenType.IDENTIFIER).value)

            self.skip_newlines()
            return ImportStatement(module_path, names=names)

        elif current.type == TokenType.IMPORT:
            # Module alias import: import module.path as alias
            self.expect(TokenType.IMPORT)

            # Parse module path (e.g., mymodule.submodule)
            module_parts = []
            module_parts.append(self.expect(TokenType.IDENTIFIER).value)
            while self.current_token().type == TokenType.DOT:
                self.advance()  # skip dot
                module_parts.append(self.expect(TokenType.IDENTIFIER).value)
            module_path = ".".join(module_parts)

            # Expect 'as' keyword
            self.expect(TokenType.AS)

            # Parse alias name
            alias = self.expect(TokenType.IDENTIFIER).value

            self.skip_newlines()
            return ImportStatement(module_path, alias=alias)

        else:
            raise SyntaxError(f"Expected 'from' or 'import', got {current.type}")

    def parse_function_def(self):
        self.expect(TokenType.DEF)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)

        parameters = []
        if self.current_token().type != TokenType.RPAREN:
            parameters.append(self.expect(TokenType.IDENTIFIER).value)
            while self.current_token().type == TokenType.COMMA:
                self.advance()
                parameters.append(self.expect(TokenType.IDENTIFIER).value)

        self.expect(TokenType.RPAREN)
        self.expect(TokenType.COLON)
        self.skip_newlines()
        self.expect(TokenType.INDENT)

        body = []
        while self.current_token().type != TokenType.DEDENT:
            body.append(self.parse_statement())
            self.skip_newlines()

        self.expect(TokenType.DEDENT)
        self.skip_newlines()

        return FunctionDef(name, parameters, body)

    def parse_if_statement(self):
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.skip_newlines()
        self.expect(TokenType.INDENT)

        then_block = []
        while self.current_token().type != TokenType.DEDENT:
            then_block.append(self.parse_statement())
            self.skip_newlines()

        self.expect(TokenType.DEDENT)
        self.skip_newlines()

        else_block = []
        if self.current_token().type == TokenType.ELSE:
            self.advance()
            self.expect(TokenType.COLON)
            self.skip_newlines()
            self.expect(TokenType.INDENT)

            while self.current_token().type != TokenType.DEDENT:
                else_block.append(self.parse_statement())
                self.skip_newlines()

            self.expect(TokenType.DEDENT)
            self.skip_newlines()

        return IfStatement(condition, then_block, else_block)

    def parse_while_statement(self):
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.skip_newlines()
        self.expect(TokenType.INDENT)

        body = []
        while self.current_token().type != TokenType.DEDENT:
            body.append(self.parse_statement())
            self.skip_newlines()

        self.expect(TokenType.DEDENT)
        self.skip_newlines()

        return WhileStatement(condition, body)

    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_addition()

        while self.current_token().type in (
            TokenType.EQUAL_EQUAL,
            TokenType.LESS,
            TokenType.GREATER,
        ):
            op = self.current_token().value
            self.advance()
            right = self.parse_addition()
            left = BinaryOp(left, op, right)

        return left

    def parse_addition(self):
        left = self.parse_multiplication()

        while self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token().value
            self.advance()
            right = self.parse_multiplication()
            left = BinaryOp(left, op, right)

        return left

    def parse_multiplication(self):
        left = self.parse_primary()

        while self.current_token().type in (TokenType.STAR, TokenType.SLASH):
            op = self.current_token().value
            self.advance()
            right = self.parse_primary()
            left = BinaryOp(left, op, right)

        return left

    def parse_primary(self):
        # Number
        if self.current_token().type == TokenType.NUMBER:
            value = self.current_token().value
            self.advance()
            return Number(value)

        # String
        if self.current_token().type == TokenType.STRING:
            value = self.current_token().value
            self.advance()
            return String(value)

        # Variable or function call (possibly dotted, e.g., alias.func)
        if self.current_token().type == TokenType.IDENTIFIER:
            name = self.current_token().value
            self.advance()

            # Handle dotted names (e.g., ops.plus)
            while self.current_token().type == TokenType.DOT:
                self.advance()  # skip dot
                name += "." + self.expect(TokenType.IDENTIFIER).value

            # Function call
            if self.current_token().type == TokenType.LPAREN:
                self.advance()
                arguments = []

                if self.current_token().type != TokenType.RPAREN:
                    arguments.append(self.parse_expression())
                    while self.current_token().type == TokenType.COMMA:
                        self.advance()
                        arguments.append(self.parse_expression())

                self.expect(TokenType.RPAREN)
                return Call(name, arguments)

            # Variable
            return Variable(name)

        # Parenthesized expression
        if self.current_token().type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        # List literal
        if self.current_token().type == TokenType.LBRACKET:
            self.advance()
            elements = []

            if self.current_token().type != TokenType.RBRACKET:
                elements.append(self.parse_expression())
                while self.current_token().type == TokenType.COMMA:
                    self.advance()
                    elements.append(self.parse_expression())

            self.expect(TokenType.RBRACKET)
            return ListLiteral(elements)

        # Dictionary literal
        if self.current_token().type == TokenType.LBRACE:
            self.advance()
            pairs = []

            if self.current_token().type != TokenType.RBRACE:
                # Parse first key-value pair
                key = self.parse_expression()
                self.expect(TokenType.COLON)
                value = self.parse_expression()
                pairs.append((key, value))

                # Parse remaining pairs
                while self.current_token().type == TokenType.COMMA:
                    self.advance()
                    # Allow trailing comma
                    if self.current_token().type == TokenType.RBRACE:
                        break
                    key = self.parse_expression()
                    self.expect(TokenType.COLON)
                    value = self.parse_expression()
                    pairs.append((key, value))

            self.expect(TokenType.RBRACE)
            return DictLiteral(pairs)

        raise SyntaxError(f"Unexpected token: {self.current_token()}")
