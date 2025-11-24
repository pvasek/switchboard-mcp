from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Keywords
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DEF = auto()
    RETURN = auto()
    FROM = auto()
    IMPORT = auto()
    AS = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    LESS = auto()
    GREATER = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 0
        self.at_line_start = True
        self.indent_stack = [0]  # Stack of indentation levels
        self.keywords = {
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "while": TokenType.WHILE,
            "def": TokenType.DEF,
            "return": TokenType.RETURN,
            "from": TokenType.FROM,
            "import": TokenType.IMPORT,
            "as": TokenType.AS,
        }

    def current_char(self):
        if self.pos >= len(self.source):
            return ""
        return self.source[self.pos]

    def advance(self):
        if self.current_char() == "\n":
            self.line += 1
            self.column = 0
            self.at_line_start = True
        else:
            self.column += 1
        self.pos += 1

    def skip_whitespace(self):
        # Only skip inline whitespace, not leading whitespace at line start
        while self.current_char() in " \t\r" and not self.at_line_start:
            self.advance()

    def handle_indentation(self):
        """Handle indentation at the start of a line, return INDENT/DEDENT tokens"""
        if not self.at_line_start:
            return []

        # Count leading spaces/tabs
        indent_level = 0
        while self.current_char() in " \t":
            if self.current_char() == " ":
                indent_level += 1
            else:  # tab
                indent_level += 4  # treat tab as 4 spaces
            self.advance()

        self.at_line_start = False

        # Skip blank lines and comments
        if self.current_char() in "\n#" or not self.current_char():
            return []

        tokens = []
        current_indent = self.indent_stack[-1]

        if indent_level > current_indent:
            # Indentation increased
            self.indent_stack.append(indent_level)
            tokens.append(Token(TokenType.INDENT, None, self.line))
        elif indent_level < current_indent:
            # Indentation decreased - may need multiple DEDENTs
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                tokens.append(Token(TokenType.DEDENT, None, self.line))

            if self.indent_stack[-1] != indent_level:
                raise SyntaxError(f"Indentation error at line {self.line}")

        return tokens

    def read_number(self):
        num = ""
        while self.current_char() and self.current_char().isdigit():
            num += self.current_char()
            self.advance()
        return int(num)

    def read_identifier(self):
        ident = ""
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == "_"):
            ident += self.current_char()
            self.advance()
        return ident

    def read_string(self, quote_char):
        self.advance()  # skip opening quote
        string = ""
        while self.current_char() and self.current_char() != quote_char:
            string += self.current_char()
            self.advance()
        self.advance()  # skip closing quote
        return string

    def tokenize(self):
        tokens = []

        while self.current_char():
            # Handle indentation at line start
            indent_tokens = self.handle_indentation()
            tokens.extend(indent_tokens)

            self.skip_whitespace()

            if not self.current_char():
                break

            # Numbers
            if self.current_char().isdigit():
                tokens.append(Token(TokenType.NUMBER, self.read_number(), self.line))

            # Identifiers and keywords
            elif self.current_char().isalpha() or self.current_char() == "_":
                ident = self.read_identifier()
                token_type = self.keywords.get(ident, TokenType.IDENTIFIER)
                tokens.append(Token(token_type, ident, self.line))

            # Strings (both single and double quotes)
            elif self.current_char() == "\"":
                tokens.append(Token(TokenType.STRING, self.read_string("\""), self.line))
            elif self.current_char() == "'":
                tokens.append(Token(TokenType.STRING, self.read_string("'"), self.line))

            # Operators and punctuation
            elif self.current_char() == "+":
                tokens.append(Token(TokenType.PLUS, "+", self.line))
                self.advance()
            elif self.current_char() == "-":
                tokens.append(Token(TokenType.MINUS, "-", self.line))
                self.advance()
            elif self.current_char() == "*":
                tokens.append(Token(TokenType.STAR, "*", self.line))
                self.advance()
            elif self.current_char() == "/":
                tokens.append(Token(TokenType.SLASH, "/", self.line))
                self.advance()
            elif self.current_char() == "=":
                self.advance()
                if self.current_char() == "=":
                    tokens.append(Token(TokenType.EQUAL_EQUAL, "==", self.line))
                    self.advance()
                else:
                    tokens.append(Token(TokenType.EQUAL, "=", self.line))
            elif self.current_char() == "<":
                tokens.append(Token(TokenType.LESS, "<", self.line))
                self.advance()
            elif self.current_char() == ">":
                tokens.append(Token(TokenType.GREATER, ">", self.line))
                self.advance()
            elif self.current_char() == "(":
                tokens.append(Token(TokenType.LPAREN, "(", self.line))
                self.advance()
            elif self.current_char() == ")":
                tokens.append(Token(TokenType.RPAREN, ")", self.line))
                self.advance()
            elif self.current_char() == "{":
                tokens.append(Token(TokenType.LBRACE, "{", self.line))
                self.advance()
            elif self.current_char() == "}":
                tokens.append(Token(TokenType.RBRACE, "}", self.line))
                self.advance()
            elif self.current_char() == "[":
                tokens.append(Token(TokenType.LBRACKET, "[", self.line))
                self.advance()
            elif self.current_char() == "]":
                tokens.append(Token(TokenType.RBRACKET, "]", self.line))
                self.advance()
            elif self.current_char() == ",":
                tokens.append(Token(TokenType.COMMA, ",", self.line))
                self.advance()
            elif self.current_char() == ".":
                tokens.append(Token(TokenType.DOT, ".", self.line))
                self.advance()
            elif self.current_char() == ":":
                tokens.append(Token(TokenType.COLON, ":", self.line))
                self.advance()
            elif self.current_char() == "\n":
                tokens.append(Token(TokenType.NEWLINE, "\n", self.line))
                self.advance()
            else:
                raise SyntaxError(f"Unexpected character: {self.current_char()} at line {self.line}")

        # Add DEDENT tokens for any remaining indentation levels
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, None, self.line))

        tokens.append(Token(TokenType.EOF, None, self.line))
        return tokens
