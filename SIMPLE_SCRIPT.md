# Simple Script

A simple lexer, parser, and interpreter for a Python-like subset language.

## Supported Features

### Imports
- **Selective imports**: Import specific functions from modules
  ```python
  from mymodule import func1
  from mymodule.submodule import func1, func2
  ```

### Builtin Functions
- **Automatic availability**: Builtin functions are available without importing
- **Tool integration**: Builtins are tools with names starting with `builtins_`
  - Example: `builtins_print` is available as `print()`
  - Example: `builtins_liquid_template_as_str` is available as `liquid_template_as_str()`
- **Precedence**: Imported functions override builtins with the same name
  ```python
  # Using a builtin (no import needed)
  result = print("Hello, World!")

  # Importing overrides the builtin
  from io import print
  result = print("Uses custom print")  # Uses io.print, not builtins_print
  ```

### Data Types
- **Numbers**: Integer literals (e.g., `42`, `100`)
- **Strings**: Double-quoted strings (e.g., `"hello"`)
- **Lists**: List literals with square brackets (e.g., `[1, 2, 3]`, `[10, 20, 30]`)
- **Variables**: Named identifiers (e.g., `x`, `count`, `my_var`)

### Operators
- **Arithmetic**: `+`, `-`, `*`, `/`
- **Comparison**: `==`, `<`, `>`
- **Assignment**: `=`

### Control Flow
- **If/Else**: Conditional branching with optional else block
  ```python
  if x > 5:
      print("greater than 5")
  else:
      print("5 or less")
  ```

- **While Loops**: Condition-based iteration
  ```python
  count = 0
  while count < 10:
      count = count + 1
  ```

### Functions
- **Definition**: Named functions with parameters
  ```python
  def add(a, b):
      return a + b
  ```

- **Calls**: Function invocation with arguments
  ```python
  result = add(5, 3)
  print(result)
  ```

## Example Program

```python
# Import functions from other modules
from math.utils import factorial
from io.display import print_result

# Calculate factorial
def calculate():
    num = 5
    fact = factorial(num)
    print_result("Factorial of", num, "is", fact)

    # Conditional example using builtin print (no import needed)
    if fact > 100:
        print("Large factorial!")  # Uses builtins_print
    else:
        print("Small factorial")   # Uses builtins_print

# Alternative: define factorial locally
def factorial_local(n):
    result = 1
    counter = 1
    while counter < n:
        counter = counter + 1
        result = result * counter
    return result

# Example with list literal and builtin
numbers = [1, 2, 3, 4, 5]
print("Numbers created")  # Builtin function, automatically available
```

## Architecture

### Lexer (Tokenization)
- Converts source code into tokens
- Handles whitespace, numbers, identifiers, strings, and operators
- Tracks line numbers for error reporting
- Recognizes keywords: `if`, `else`, `while`, `def`, `return`

### Parser (AST Generation)
- Converts tokens into Abstract Syntax Tree (AST)
- Supports expression precedence: comparison → addition → multiplication → primary
- Parses statements: assignments, function definitions, control flow, returns

### AST Node Types
- **Expressions**: Number, String, Variable, BinaryOp, Call, ListLiteral
- **Statements**: ImportStatement, Assignment, IfStatement, WhileStatement, FunctionDef, Return, ExpressionStatement

### Interpreter (Execution)
- Evaluates the AST and executes the program
- Manages variable environment and function definitions
- Supports tool integration:
  - **Regular tools**: Imported tools map to external tool functions
    - Example: `from math.statistics import min` maps to tool named `math_statistics_min`
  - **Builtin tools**: Tools prefixed with `builtins_` are automatically available
    - Example: Tool named `builtins_print` is available as `print()` without import
    - Imported functions take precedence over builtins with the same name
- Returns the value of the last expression evaluated

## Syntax Notes
- Blocks use indentation (spaces or tabs)
- Block headers end with colon `:`
- Conditions do NOT use parentheses
- Statements are newline-terminated
- Function parameters and call arguments are comma-separated
