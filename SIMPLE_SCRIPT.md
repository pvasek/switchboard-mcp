# Simple Script

A simple lexer, parser, and interpreter for a Python-like subset language.

## Supported Features

### Imports
- **Selective imports**: Import specific functions from modules
  ```python
  from mymodule import func1
  from mymodule.submodule import func1, func2
  ```

- **Module aliases**: Import modules with aliases for easier access
  ```python
  import module as m
  import module.submodule as s

  # Use the alias to call functions
  result = m.function_name(arg1, arg2)
  value = s.another_function(arg)
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
- **Strings**: Single or double-quoted strings (e.g., `"hello"`, `'world'`)
- **Lists**: List literals with square brackets (e.g., `[1, 2, 3]`, `[10, 20, 30]`)
  - Empty lists: `[]`
  - Lists with expressions: `[1 + 2, 3 * 4]`
  - Nested lists: `[[1, 2], [3, 4]]`
  - Mixed-type lists: `[1, "hello", x]`
- **Dictionaries**: Dictionary literals with curly braces (e.g., `{"key": "value"}`)
  - Empty dicts: `{}`
  - String keys: `{"name": "Alice", "age": 30}`
  - Variable keys: `{x: 1, y: 2}`
  - Expression keys: `{1 + 1: "two"}`
  - Nested dicts: `{"outer": {"inner": "value"}}`
  - Mixed values: `{"num": 42, "list": [1, 2, 3]}`
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

### Lists

Lists are ordered collections that can hold any type of value.

- **Empty lists**: Create an empty list
  ```python
  empty = []
  ```

- **List literals**: Create lists with initial values
  ```python
  numbers = [1, 2, 3, 4, 5]
  names = ["Alice", "Bob", "Charlie"]
  mixed = [1, "hello", 42]
  ```

- **Lists with expressions**: List elements can be any expression
  ```python
  x = 10
  y = 20
  calculations = [x + y, x * 2, y / 2]  # [30, 20, 10.0]
  ```

- **Nested lists**: Lists can contain other lists
  ```python
  matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
  pairs = [[1, 2], [3, 4], [5, 6]]
  ```

- **Lists as function arguments**: Pass lists to imported functions
  ```python
  from math.statistics import min, max, average

  numbers = [5, 2, 8, 1, 9, 3]
  smallest = min(numbers)        # 1
  largest = max(numbers)          # 9
  avg = average(numbers)          # 4.666...
  ```

- **Multiple list arguments**: Functions can accept multiple lists
  ```python
  from list.operations import concat

  list1 = [1, 2, 3]
  list2 = [4, 5, 6]
  combined = concat(list1, list2)  # [1, 2, 3, 4, 5, 6]
  ```

- **Mixed arguments**: Combine scalars and lists
  ```python
  from list.operations import prepend, append

  items = [2, 3, 4]
  with_first = prepend(1, items)   # [1, 2, 3, 4]
  with_last = append(items, 5)     # [2, 3, 4, 5]
  ```

### Dictionaries

Dictionaries are key-value mappings that allow efficient data organization.

- **Empty dictionaries**: Create an empty dictionary
  ```python
  empty = {}
  ```

- **Dictionary literals**: Create dictionaries with initial key-value pairs
  ```python
  person = {"name": "Alice", "age": 30, "city": "NYC"}
  config = {"host": "localhost", "port": 8080, "debug": 1}
  ```

- **Variable keys**: Keys can be variables or expressions
  ```python
  key1 = "username"
  key2 = "password"
  credentials = {key1: "admin", key2: "secret"}
  ```

- **Expression keys**: Keys can be any expression
  ```python
  # Numeric expression keys
  lookup = {1 + 1: "two", 2 + 2: "four", 3 + 3: "six"}

  # String expression keys
  prefix = "user_"
  data = {prefix: "value"}  # {"user_": "value"}
  ```

- **Various value types**: Values can be any type
  ```python
  mixed = {
      "number": 42,
      "text": "hello",
      "list": [1, 2, 3],
      "nested": {"inner": "value"}
  }
  ```

- **Nested dictionaries**: Dictionaries can contain other dictionaries
  ```python
  config = {
      "database": {
          "host": "localhost",
          "port": 5432
      },
      "cache": {
          "enabled": 1,
          "ttl": 300
      }
  }
  ```

- **Dictionaries as function arguments**: Pass dictionaries to imported functions
  ```python
  from json import stringify, parse
  from data.utils import getkeys, merge

  # Stringify a dictionary
  person = {"name": "Bob", "age": 35}
  json_str = stringify(person)

  # Get all keys
  keys = getkeys(person)  # ["name", "age"]

  # Merge dictionaries
  defaults = {"theme": "dark", "lang": "en"}
  user_prefs = {"theme": "light"}
  settings = merge(defaults, user_prefs)  # {"theme": "light", "lang": "en"}
  ```

- **Multiple dictionary arguments**: Functions can accept multiple dictionaries
  ```python
  from data.utils import merge, compare

  dict1 = {"a": 1, "b": 2}
  dict2 = {"c": 3, "d": 4}
  combined = merge(dict1, dict2)  # {"a": 1, "b": 2, "c": 3, "d": 4}
  ```

- **Mixed arguments**: Combine scalars, lists, and dictionaries
  ```python
  from data.operations import update, transform

  base = {"status": "active"}
  enriched = update("timestamp", 12345, base)
  # {"status": "active", "timestamp": 12345}
  ```

- **Key constraints**: Dictionary keys must be hashable
  ```python
  # Valid keys: numbers, strings
  valid = {1: "one", "key": "value", 42: "answer"}

  # Invalid: lists as keys (will raise RuntimeError)
  # invalid = {[1, 2]: "value"}  # Error!
  ```

## Example Program

```python
# Import functions from other modules (selective imports)
from math.utils import factorial
from math.statistics import min, max, average
from io.display import print_result

# Import modules with aliases
import math.operations as ops
import math.random as rand

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

# List examples with builtin and imported functions
numbers = [1, 2, 3, 4, 5]
print("Numbers created")  # Builtin function, automatically available

# Using lists with imported functions
scores = [85, 92, 78, 95, 88]
lowest = min(scores)
highest = max(scores)
avg_score = average(scores)

print("Score analysis complete")

# Nested list example
matrix = [[1, 2], [3, 4], [5, 6]]

# List with expressions and variables
a = 10
b = 20
calculated = [a + b, a * 2, b / 2]

# Using module aliases
sum_result = ops.plus(a, b)          # Using aliased module
product = ops.multiply(a, b)         # math.operations.multiply via 'ops' alias
random_nums = rand.generate_list(5, 1, 100)  # math.random.generate_list via 'rand' alias

# Dictionary examples
person = {"name": "David", "age": 28, "role": "developer"}
print("Person record created")

# Nested dictionary
settings = {
    "app": {
        "name": "MyApp",
        "version": "1.0"
    },
    "features": {
        "darkMode": 1,
        "notifications": 1
    }
}

# Dictionary with mixed types
data = {
    "id": 12345,
    "tags": ["python", "scripting"],
    "meta": {"created": "2025-01-01"}
}
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
- Handles two import styles:
  - Selective imports: `from module.submodule import func1, func2`
  - Module aliases: `import module.submodule as alias`

### AST Node Types
- **Expressions**: Number, String, Variable, BinaryOp, Call, ListLiteral
- **Statements**: ImportStatement, Assignment, IfStatement, WhileStatement, FunctionDef, Return, ExpressionStatement

### Interpreter (Execution)
- Evaluates the AST and executes the program
- Manages variable environment and function definitions
- Supports tool integration:
  - **Regular tools**: Imported tools map to external tool functions
    - Example: `from math.statistics import min` maps to tool named `math_statistics_min`
  - **Module aliases**: Aliased modules allow accessing tools via dot notation
    - Example: `import math.operations as ops` then `ops.plus(1, 2)` maps to tool `math_operations_plus`
    - Alias is stored in environment and resolved at call time
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
