"""Unit tests for refactored utils functions."""

import pytest

from simple_script.tools import Tool, ToolParameter
from switchboard_mcp.utils import (
    Folder,
    _format_function_description,
    _format_type_from_schema,
    _json_type_to_python,
    browse_tools,
)


class TestFormatFunctionDescription:
    """Test suite for _format_function_description function."""

    def test_regular_tool_with_types(self):
        """Test regular tool with typed parameters."""
        tool = Tool(
            name="math_operations_plus",
            func=None,
            description="Add two numbers together",
            parameters=[
                ToolParameter(name="x", type="number"),
                ToolParameter(name="y", type="number"),
            ],
        )
        result = _format_function_description(tool)
        assert result == "plus(x: number, y: number): Add two numbers together"

    def test_builtin_tool(self):
        """Test builtin tool (with builtins_ prefix)."""
        tool = Tool(
            name="builtins_print",
            func=None,
            description="Print text to output",
            parameters=[ToolParameter(name="text", type="string")],
        )
        result = _format_function_description(tool)
        assert result == "print(text: string): Print text to output"

    def test_builtin_with_underscores(self):
        """Test builtin tool with underscores in name."""
        tool = Tool(
            name="builtins_liquid_template_as_str",
            func=None,
            description="Render a liquid template",
            parameters=[
                ToolParameter(name="template", type="string"),
                ToolParameter(name="data", type="string"),
            ],
        )
        result = _format_function_description(tool)
        # Should strip "builtins_" and show the rest
        assert result == "liquid_template_as_str(template: string, data: string): Render a liquid template"

    def test_tool_without_types(self):
        """Test tool with parameters but no type annotations."""
        tool = Tool(
            name="utils_helper_func",
            func=None,
            description="Helper function",
            parameters=[
                ToolParameter(name="arg1", type=None),
                ToolParameter(name="arg2", type=None),
            ],
        )
        result = _format_function_description(tool)
        assert result == "func(arg1, arg2): Helper function"

    def test_tool_no_parameters(self):
        """Test tool with no parameters."""
        tool = Tool(
            name="utils_get_version",
            func=None,
            description="Get current version",
            parameters=None,
        )
        result = _format_function_description(tool)
        assert result == "version(): Get current version"


class TestJsonTypeToPython:
    """Test suite for _json_type_to_python function."""

    def test_string_type(self):
        """Test string type conversion."""
        schema = {"type": "string"}
        assert _json_type_to_python(schema) == "str"

    def test_integer_type(self):
        """Test integer type conversion."""
        schema = {"type": "integer"}
        assert _json_type_to_python(schema) == "int"

    def test_number_type(self):
        """Test number (float) type conversion."""
        schema = {"type": "number"}
        assert _json_type_to_python(schema) == "float"

    def test_boolean_type(self):
        """Test boolean type conversion."""
        schema = {"type": "boolean"}
        assert _json_type_to_python(schema) == "bool"

    def test_array_of_strings(self):
        """Test array type with string items."""
        schema = {"type": "array", "items": {"type": "string"}}
        assert _json_type_to_python(schema) == "list[str]"

    def test_array_of_numbers(self):
        """Test array type with number items."""
        schema = {"type": "array", "items": {"type": "number"}}
        assert _json_type_to_python(schema) == "list[float]"

    def test_array_without_items(self):
        """Test array type without items specification."""
        schema = {"type": "array"}
        assert _json_type_to_python(schema) == "list[Any]"

    def test_object_type(self):
        """Test object type (converted to dict)."""
        schema = {"type": "object"}
        assert _json_type_to_python(schema) == "dict[str, Any]"

    def test_enum_strings(self):
        """Test enum converted to Literal with strings."""
        schema = {"type": "string", "enum": ["active", "inactive", "pending"]}
        result = _json_type_to_python(schema)
        assert result == 'Literal["active", "inactive", "pending"]'

    def test_enum_numbers(self):
        """Test enum converted to Literal with numbers."""
        schema = {"type": "integer", "enum": [1, 2, 3]}
        result = _json_type_to_python(schema)
        assert result == "Literal[1, 2, 3]"

    def test_unknown_type(self):
        """Test unknown type returns Any."""
        schema = {"type": "unknown"}
        assert _json_type_to_python(schema) == "Any"

    def test_no_type(self):
        """Test schema without type returns Any."""
        schema = {}
        assert _json_type_to_python(schema) == "Any"


class TestFormatTypeFromSchema:
    """Test suite for _format_type_from_schema function."""

    def test_simple_object(self):
        """Test simple object with all required fields."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"],
        }
        result = _format_type_from_schema(schema, "Person")
        assert "class PersonDict(TypedDict):" in result
        assert "name: str" in result
        assert "age: int" in result
        assert "NotRequired" not in result  # All fields required

    def test_object_with_optional_fields(self):
        """Test object with optional (not required) fields."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name"],
        }
        result = _format_type_from_schema(schema, "User")
        assert "class UserDict(TypedDict):" in result
        assert "name: str" in result
        assert "email: NotRequired[str]" in result
        assert "age: NotRequired[int]" in result

    def test_object_with_array_field(self):
        """Test object with array field."""
        schema = {
            "type": "object",
            "properties": {
                "tags": {"type": "array", "items": {"type": "string"}},
                "count": {"type": "integer"},
            },
            "required": ["tags", "count"],
        }
        result = _format_type_from_schema(schema, "Tagged")
        assert "class TaggedDict(TypedDict):" in result
        assert "tags: list[str]" in result
        assert "count: int" in result

    def test_object_with_enum(self):
        """Test object with enum field (Literal)."""
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["active", "inactive"]},
            },
            "required": ["status"],
        }
        result = _format_type_from_schema(schema, "Status")
        assert "class StatusDict(TypedDict):" in result
        assert 'status: Literal["active", "inactive"]' in result

    def test_non_object_type_returns_empty(self):
        """Test that non-object types return empty string."""
        schema = {"type": "string"}
        result = _format_type_from_schema(schema, "Test")
        assert result == ""

    def test_object_without_properties_returns_empty(self):
        """Test that object without properties returns empty string."""
        schema = {"type": "object", "properties": {}}
        result = _format_type_from_schema(schema, "Empty")
        assert result == ""

    def test_all_fields_optional(self):
        """Test object where all fields are optional."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number"},
            },
            "required": [],
        }
        result = _format_type_from_schema(schema, "Optional")
        assert "class OptionalDict(TypedDict):" in result
        assert "name: NotRequired[str]" in result
        assert "value: NotRequired[float]" in result


class TestExtractNestedTypes:
    """Test suite for _extract_nested_types function."""

    def test_extract_nested_object(self):
        """Test extracting a nested object property."""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                    },
                    "required": ["name"],
                },
                "id": {"type": "integer"},
            },
        }
        from switchboard_mcp.utils import _extract_nested_types

        result = _extract_nested_types(schema)
        assert len(result) == 1
        assert result[0][0] == "User"
        assert result[0][1]["type"] == "object"
        assert "name" in result[0][1]["properties"]

    def test_extract_array_of_objects(self):
        """Test extracting nested objects from array items."""
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "value": {"type": "string"},
                        },
                    },
                },
            },
        }
        from switchboard_mcp.utils import _extract_nested_types

        result = _extract_nested_types(schema)
        assert len(result) == 1
        assert result[0][0] == "Items"
        assert result[0][1]["type"] == "object"
        assert "id" in result[0][1]["properties"]

    def test_extract_multiple_nested_types(self):
        """Test extracting multiple nested types."""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                },
                "settings": {
                    "type": "object",
                    "properties": {"theme": {"type": "string"}},
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"label": {"type": "string"}},
                    },
                },
            },
        }
        from switchboard_mcp.utils import _extract_nested_types

        result = _extract_nested_types(schema)
        assert len(result) == 3
        type_names = [name for name, _ in result]
        assert "User" in type_names
        assert "Settings" in type_names
        assert "Tags" in type_names

    def test_extract_no_nested_types(self):
        """Test that simple properties don't generate types."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }
        from switchboard_mcp.utils import _extract_nested_types

        result = _extract_nested_types(schema)
        assert len(result) == 0


class TestBrowseToolsWithCounts:
    """Test suite for browse_tools namespace counts."""

    def test_subnamespaces_show_counts(self):
        """Test that subnamespaces show counts of their contents."""
        # Create a hierarchy: root -> api -> users (3 tools), products (3 tools)
        tools = [
            Tool(
                name="api_users_create",
                func=None,
                description="Create user",
                parameters=[ToolParameter(name="name", type="string")],
            ),
            Tool(
                name="api_users_get",
                func=None,
                description="Get user",
                parameters=[ToolParameter(name="id", type="string")],
            ),
            Tool(
                name="api_users_delete",
                func=None,
                description="Delete user",
                parameters=[ToolParameter(name="id", type="string")],
            ),
            Tool(
                name="api_products_list",
                func=None,
                description="List products",
                parameters=None,
            ),
            Tool(
                name="api_products_create",
                func=None,
                description="Create product",
                parameters=None,
            ),
            Tool(
                name="api_products_delete",
                func=None,
                description="Delete product",
                parameters=None,
            ),
        ]

        root = Folder.from_tools(tools)

        # Check root level - should show "api" with counts
        result = browse_tools(root, "")
        assert "Subnamespaces:" in result
        assert "api (subnamespaces: 2, functions: 0)" in result

        # Check api level - should show users and products with their counts
        result = browse_tools(root, "api")
        assert "Subnamespaces:" in result
        assert "api.users (subnamespaces: 0, functions: 3)" in result
        assert "api.products (subnamespaces: 0, functions: 3)" in result

    def test_nested_subnamespaces_show_counts(self):
        """Test deeply nested subnamespaces show correct counts."""
        tools = [
            Tool(
                name="browser_console_messages_get",
                func=None,
                description="Get messages",
                parameters=None,
            ),
            Tool(
                name="browser_console_errors_get",
                func=None,
                description="Get errors",
                parameters=None,
            ),
            Tool(
                name="browser_console_warnings_get",
                func=None,
                description="Get warnings",
                parameters=None,
            ),
            Tool(
                name="browser_fill_form",
                func=None,
                description="Fill form",
                parameters=None,
            ),
            Tool(
                name="browser_fill_input",
                func=None,
                description="Fill input",
                parameters=None,
            ),
            Tool(
                name="browser_fill_select",
                func=None,
                description="Fill select",
                parameters=None,
            ),
        ]

        root = Folder.from_tools(tools)

        # Check browser level
        result = browse_tools(root, "browser")
        assert "Subnamespaces:" in result
        assert "browser.console (subnamespaces: 0, functions: 3)" in result
        assert "browser.fill (subnamespaces: 0, functions: 3)" in result


class TestFolderGroupingWithThreePlusRule:
    """Test suite for Folder.from_tools() with 3+ grouping rule."""

    def test_folder_creation_with_3_plus_items(self):
        """Test that subfolder is created when 3+ tools share the same prefix."""
        tools = [
            Tool(
                name="browser_test_a",
                func=None,
                description="Test A",
                parameters=None,
            ),
            Tool(
                name="browser_test_b",
                func=None,
                description="Test B",
                parameters=None,
            ),
            Tool(
                name="browser_test_c",
                func=None,
                description="Test C",
                parameters=None,
            ),
        ]

        root = Folder.from_tools(tools)

        # Should have browser folder
        assert len(root.folders) == 1
        browser_folder = root.folders[0]
        assert browser_folder.name == "browser"

        # Browser should have test subfolder (3+ tools)
        assert len(browser_folder.folders) == 1
        test_folder = browser_folder.folders[0]
        assert test_folder.name == "test"

        # Test folder should have 3 tools
        assert len(test_folder.tools) == 3
        tool_names = [t.name for t in test_folder.tools]
        assert "browser_test_a" in tool_names
        assert "browser_test_b" in tool_names
        assert "browser_test_c" in tool_names

    def test_folder_flattening_with_less_than_3_items(self):
        """Test that no subfolder is created when < 3 tools share prefix (flattened)."""
        tools = [
            Tool(
                name="browser_test_a",
                func=None,
                description="Test A",
                parameters=None,
            ),
            Tool(
                name="browser_test_b",
                func=None,
                description="Test B",
                parameters=None,
            ),
        ]

        root = Folder.from_tools(tools)

        # Should have browser folder
        assert len(root.folders) == 1
        browser_folder = root.folders[0]
        assert browser_folder.name == "browser"

        # Browser should have NO test subfolder (< 3 tools)
        assert len(browser_folder.folders) == 0

        # Tools should be flattened directly into browser folder
        assert len(browser_folder.tools) == 2
        tool_names = [t.name for t in browser_folder.tools]
        assert "browser_test_a" in tool_names
        assert "browser_test_b" in tool_names

    def test_mixed_grouping_some_3_plus_some_less(self):
        """Test mixed scenario with some groups >= 3 and some < 3."""
        tools = [
            # test group: 3 tools (should create subfolder)
            Tool(name="browser_test_a", func=None, description="", parameters=None),
            Tool(name="browser_test_b", func=None, description="", parameters=None),
            Tool(name="browser_test_c", func=None, description="", parameters=None),
            # console group: 2 tools (should be flattened)
            Tool(name="browser_console_log", func=None, description="", parameters=None),
            Tool(name="browser_console_error", func=None, description="", parameters=None),
            # Single tool (should be flattened)
            Tool(name="browser_navigate", func=None, description="", parameters=None),
        ]

        root = Folder.from_tools(tools)

        # Should have browser folder
        assert len(root.folders) == 1
        browser_folder = root.folders[0]

        # Browser should have only test subfolder (3+ items)
        assert len(browser_folder.folders) == 1
        test_folder = browser_folder.folders[0]
        assert test_folder.name == "test"
        assert len(test_folder.tools) == 3

        # Console and navigate should be flattened into browser
        assert len(browser_folder.tools) == 3
        tool_names = [t.name for t in browser_folder.tools]
        assert "browser_console_log" in tool_names
        assert "browser_console_error" in tool_names
        assert "browser_navigate" in tool_names

    def test_deep_nesting_with_grouping_rules(self):
        """Test multi-level nesting with grouping rules applied at each level."""
        tools = [
            # api.users group: 3 tools (should create subfolder)
            Tool(name="api_users_create", func=None, description="", parameters=None),
            Tool(name="api_users_delete", func=None, description="", parameters=None),
            Tool(name="api_users_update", func=None, description="", parameters=None),
            # api.auth group: 2 tools (should be flattened)
            Tool(name="api_auth_login", func=None, description="", parameters=None),
            Tool(name="api_auth_logout", func=None, description="", parameters=None),
        ]

        root = Folder.from_tools(tools)

        # Should have api folder
        assert len(root.folders) == 1
        api_folder = root.folders[0]
        assert api_folder.name == "api"

        # API should have users subfolder (3+ items)
        assert len(api_folder.folders) == 1
        users_folder = api_folder.folders[0]
        assert users_folder.name == "users"
        assert len(users_folder.tools) == 3

        # Auth should be flattened into api
        assert len(api_folder.tools) == 2
        tool_names = [t.name for t in api_folder.tools]
        assert "api_auth_login" in tool_names
        assert "api_auth_logout" in tool_names

    def test_builtins_unaffected_by_grouping_rule(self):
        """Test that builtin tools are still added to root, unaffected by grouping."""
        tools = [
            Tool(name="builtins_print", func=None, description="", parameters=None),
            Tool(name="builtins_log", func=None, description="", parameters=None),
            Tool(name="browser_navigate", func=None, description="", parameters=None),
        ]

        root = Folder.from_tools(tools)

        # Root should have 2 builtin tools
        assert len(root.tools) == 2
        builtin_names = [t.name for t in root.tools]
        assert "builtins_print" in builtin_names
        assert "builtins_log" in builtin_names

        # Should still have browser folder
        assert len(root.folders) == 1
        assert root.folders[0].name == "browser"

    def test_exactly_3_items_creates_folder(self):
        """Test boundary condition: exactly 3 items should create folder."""
        tools = [
            Tool(name="math_calc_add", func=None, description="", parameters=None),
            Tool(name="math_calc_sub", func=None, description="", parameters=None),
            Tool(name="math_calc_mul", func=None, description="", parameters=None),
        ]

        root = Folder.from_tools(tools)

        # Should have math folder with calc subfolder
        math_folder = root.folders[0]
        assert len(math_folder.folders) == 1
        calc_folder = math_folder.folders[0]
        assert calc_folder.name == "calc"
        assert len(calc_folder.tools) == 3

    def test_single_tool_flattened(self):
        """Test that single tool with multiple underscores is flattened."""
        tools = [
            Tool(name="browser_console_log", func=None, description="", parameters=None),
        ]

        root = Folder.from_tools(tools)

        # Should have browser folder
        browser_folder = root.folders[0]

        # No console subfolder (only 1 tool)
        assert len(browser_folder.folders) == 0

        # Tool flattened into browser
        assert len(browser_folder.tools) == 1
        assert browser_folder.tools[0].name == "browser_console_log"


class TestBrowseToolsWithTypes:
    """Test suite for browse_tools integration with types."""

    def test_tool_with_simple_root_schema_no_types(self):
        """Test that tools with simple root inputSchema don't show type definitions."""
        tools = [
            Tool(
                name="api_users_create",
                func=None,
                description="Create a new user",
                parameters=[ToolParameter(name="name", type="string"), ToolParameter(name="email", type="string")],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                    },
                    "required": ["name", "email"],
                },
            ),
            Tool(name="api_users_get", func=None, description="Get user", parameters=None),
            Tool(name="api_users_delete", func=None, description="Delete user", parameters=None),
        ]

        # Build folder structure using Folder.from_tools
        root = Folder.from_tools(tools)

        # Navigate to api.users folder where the tool should be (3+ tools = subfolder)
        result = browse_tools(root, "api.users")

        # Should NOT show Types section (root schema is already in function params)
        assert "Types:" not in result

        # Should show Functions section
        assert "Functions:" in result
        assert "create(name: string, email: string): Create a new user" in result

    def test_tool_with_nested_object_shows_type(self):
        """Test that tools with nested objects in inputSchema show type definitions."""
        tools = [
            Tool(
                name="api_users_create",
                func=None,
                description="Create a new user",
                parameters=[ToolParameter(name="user", type="object")],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                            },
                            "required": ["name", "email"],
                        },
                    },
                    "required": ["user"],
                },
            ),
            Tool(name="api_users_get", func=None, description="Get user", parameters=None),
            Tool(name="api_users_delete", func=None, description="Delete user", parameters=None),
        ]

        # Build folder structure using Folder.from_tools
        root = Folder.from_tools(tools)

        # Navigate to api.users folder where the tool should be (3+ tools = subfolder)
        result = browse_tools(root, "api.users")

        # Should show Types section with the nested TypedDict
        assert "Types:" in result
        assert "class UserDict(TypedDict):" in result
        assert "name: str" in result
        assert "email: str" in result

        # Should also show Functions section
        assert "Functions:" in result
        assert "create(user: object): Create a new user" in result

    def test_tool_without_object_schema_no_type(self):
        """Test that tools without object inputSchema don't show type definitions."""
        tools = [
            Tool(
                name="api_users_get",
                func=None,
                description="Get user by ID",
                parameters=[ToolParameter(name="user_id", type="string")],
                inputSchema=None,
            ),
            Tool(name="api_users_create", func=None, description="Create user", parameters=None),
            Tool(name="api_users_delete", func=None, description="Delete user", parameters=None),
        ]

        root = Folder.from_tools(tools)
        result = browse_tools(root, "api.users")

        # Should NOT show Types section
        assert "Types:" not in result

        # Should show Functions section
        assert "Functions:" in result
        assert "get(user_id: string): Get user by ID" in result

    def test_tool_with_array_of_objects_shows_type(self):
        """Test that tools with array of objects show type definitions."""
        tools = [
            Tool(
                name="data_records_create",
                func=None,
                description="Create multiple records",
                parameters=[ToolParameter(name="records", type="list")],
                inputSchema={
                    "type": "object",
                    "properties": {
                        "records": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "value": {"type": "string"},
                                },
                                "required": ["id"],
                            },
                        },
                    },
                    "required": ["records"],
                },
            ),
            Tool(name="data_records_get", func=None, description="Get record", parameters=None),
            Tool(name="data_records_delete", func=None, description="Delete record", parameters=None),
        ]

        root = Folder.from_tools(tools)
        result = browse_tools(root, "data.records")

        # Should show Types section for array items
        assert "Types:" in result
        assert "class RecordsDict(TypedDict):" in result
        assert "id: int" in result
        assert "value: NotRequired[str]" in result

        # Should show function
        assert "Functions:" in result
        assert "create(records: list): Create multiple records" in result

    def test_mixed_tools_with_and_without_nested_types(self):
        """Test browsing folder with mix of tools with/without nested types."""
        tool_with_nested = Tool(
            name="data_records_create",
            func=None,
            description="Create record",
            parameters=[ToolParameter(name="record", type="object")],
            inputSchema={
                "type": "object",
                "properties": {
                    "record": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "value": {"type": "string"},
                        },
                        "required": ["id"],
                    },
                },
                "required": ["record"],
            },
        )

        tool_without_nested = Tool(
            name="data_records_delete",
            func=None,
            description="Delete record",
            parameters=[ToolParameter(name="id", type="integer")],
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                },
                "required": ["id"],
            },
        )

        # Add third tool to meet 3+ threshold
        tool_extra = Tool(
            name="data_records_update",
            func=None,
            description="Update record",
            parameters=None,
        )

        root = Folder.from_tools([tool_with_nested, tool_without_nested, tool_extra])
        result = browse_tools(root, "data.records")

        # Should show Types section only for tool_with_nested
        assert "Types:" in result
        assert "class RecordDict(TypedDict):" in result
        assert "id: int" in result
        assert "value: NotRequired[str]" in result

        # Should show both functions
        assert "Functions:" in result
        assert "create(record: object): Create record" in result
        assert "delete(id: integer): Delete record" in result
