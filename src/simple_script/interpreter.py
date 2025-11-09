from typing import Any

from simple_script.lexer import Lexer
from simple_script.parser import (
    Assignment,
    ASTNode,
    BinaryOp,
    Call,
    ExpressionStatement,
    FunctionDef,
    IfStatement,
    ImportStatement,
    ListLiteral,
    Number,
    Parser,
    Return,
    String,
    Variable,
    WhileStatement,
)
from simple_script.tools import Tool


class Interpreter:
    def __init__(self, tools: list[Tool]):
        self.tools = tools
        self.tool_map, self.builtin_map = self._build_tool_maps()
        self.env = {}  # Variable environment
        self.functions = {}  # User-defined functions
        self.last_value = None

    def _build_tool_maps(self) -> tuple[dict[str, Tool], dict[str, Tool]]:
        """Build maps for regular tools and builtin tools"""
        tool_map = {}
        builtin_map = {}

        for tool in self.tools:
            # Check if it's a builtin (starts with "builtins_")
            if tool.name.startswith("builtins_"):
                # Extract the function name after "builtins_"
                func_name = tool.name[len("builtins_") :]
                builtin_map[func_name] = tool
            else:
                # Convert "math_statistics_min" to "math.statistics.min"
                parts = tool.name.split("_")
                # The last part is the function name
                func_name = parts[-1]
                # The rest is the module path
                module_path = ".".join(parts[:-1])
                full_path = f"{module_path}.{func_name}"
                tool_map[full_path] = tool

        return tool_map, builtin_map

    def evaluate(self, script: str) -> Any:
        """Evaluate a script and return the result"""
        # Parse the script
        lexer = Lexer(script)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # Execute all statements
        for statement in ast:
            self.last_value = self._execute_statement(statement)

        return self.last_value

    def _execute_statement(self, node: ASTNode) -> Any:
        """Execute a statement and return its value"""
        if isinstance(node, ImportStatement):
            return self._execute_import(node)
        elif isinstance(node, Assignment):
            return self._execute_assignment(node)
        elif isinstance(node, IfStatement):
            return self._execute_if(node)
        elif isinstance(node, WhileStatement):
            return self._execute_while(node)
        elif isinstance(node, FunctionDef):
            return self._execute_function_def(node)
        elif isinstance(node, Return):
            return self._evaluate_expression(node.value)
        elif isinstance(node, ExpressionStatement):
            return self._evaluate_expression(node.expression)
        else:
            raise RuntimeError(f"Unknown statement type: {type(node)}")

    def _execute_import(self, node: ImportStatement) -> None:
        """Execute an import statement"""
        module_path = node.module_path
        for name in node.names:
            # Build the full path: "math.statistics.min"
            full_path = f"{module_path}.{name}"

            # Check if this corresponds to a tool
            if full_path in self.tool_map:
                # Store the tool in the environment under the imported name
                self.env[name] = self.tool_map[full_path]
            else:
                raise RuntimeError(f"Tool '{full_path}' not found")

        return None

    def _execute_assignment(self, node: Assignment) -> Any:
        """Execute an assignment statement"""
        value = self._evaluate_expression(node.value)
        self.env[node.name] = value
        return value

    def _execute_if(self, node: IfStatement) -> Any:
        """Execute an if statement"""
        condition = self._evaluate_expression(node.condition)

        if self._is_truthy(condition):
            result = None
            for stmt in node.then_block:
                result = self._execute_statement(stmt)
            return result
        else:
            result = None
            for stmt in node.else_block:
                result = self._execute_statement(stmt)
            return result

    def _execute_while(self, node: WhileStatement) -> Any:
        """Execute a while loop"""
        result = None
        while self._is_truthy(self._evaluate_expression(node.condition)):
            for stmt in node.body:
                result = self._execute_statement(stmt)
        return result

    def _execute_function_def(self, node: FunctionDef) -> None:
        """Store a function definition"""
        self.functions[node.name] = node
        return None

    def _evaluate_expression(self, node: ASTNode) -> Any:
        """Evaluate an expression and return its value"""
        if isinstance(node, Number):
            return node.value
        elif isinstance(node, String):
            return node.value
        elif isinstance(node, Variable):
            if node.name not in self.env:
                raise RuntimeError(f"Variable '{node.name}' not defined")
            return self.env[node.name]
        elif isinstance(node, BinaryOp):
            return self._evaluate_binary_op(node)
        elif isinstance(node, Call):
            return self._evaluate_call(node)
        elif isinstance(node, ListLiteral):
            return [self._evaluate_expression(elem) for elem in node.elements]
        else:
            raise RuntimeError(f"Unknown expression type: {type(node)}")

    def _evaluate_binary_op(self, node: BinaryOp) -> Any:
        """Evaluate a binary operation"""
        left = self._evaluate_expression(node.left)
        right = self._evaluate_expression(node.right)

        if node.operator == "+":
            return left + right
        elif node.operator == "-":
            return left - right
        elif node.operator == "*":
            return left * right
        elif node.operator == "/":
            return left / right
        elif node.operator == "==":
            return left == right
        elif node.operator == "<":
            return left < right
        elif node.operator == ">":
            return left > right
        else:
            raise RuntimeError(f"Unknown operator: {node.operator}")

    def _evaluate_call(self, node: Call) -> Any:
        """Evaluate a function call"""
        # Evaluate arguments
        args = [self._evaluate_expression(arg) for arg in node.arguments]

        # Check if it's a user-defined function
        if node.function in self.functions:
            return self._call_user_function(node.function, args)

        # Check if it's a tool (imported function) - imported tools take precedence over builtins
        if node.function in self.env:
            obj = self.env[node.function]
            if isinstance(obj, Tool):
                return obj.func(*args)
            else:
                raise RuntimeError(f"'{node.function}' is not callable")

        # Check if it's a builtin function
        if node.function in self.builtin_map:
            builtin_tool = self.builtin_map[node.function]
            return builtin_tool.func(*args)

        raise RuntimeError(f"Function '{node.function}' not defined")

    def _call_user_function(self, name: str, args: list[Any]) -> Any:
        """Call a user-defined function"""
        func_def = self.functions[name]

        if len(args) != len(func_def.parameters):
            raise RuntimeError(
                f"Function '{name}' expects {len(func_def.parameters)} arguments, got {len(args)}"
            )

        # Save current environment
        old_env = self.env.copy()

        # Bind parameters to arguments
        for param, arg in zip(func_def.parameters, args):
            self.env[param] = arg

        # Execute function body
        result = None
        for stmt in func_def.body:
            result = self._execute_statement(stmt)
            # Check for return statement
            if isinstance(stmt, Return):
                break

        # Restore environment
        self.env = old_env

        return result

    def _is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy"""
        if isinstance(value, bool):
            return value
        if isinstance(value, int) or isinstance(value, float):
            return value != 0
        if value is None:
            return False
        return True
