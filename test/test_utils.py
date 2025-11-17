"""Unit tests for refactored utils functions."""

import pytest

from simple_script.tools import Tool, ToolParameter
from switchboard_mcp.config import MCPServerConfig, NamespaceMapping, StdioConfig
from switchboard_mcp.session_manager import ToolGroup
from switchboard_mcp.utils import (
    Folder,
    _format_function_description,
    _format_type_from_schema,
    _json_type_to_python,
    browse_tools,
)


def create_tool_group(tools: list[Tool], namespace_mappings: list[NamespaceMapping] | None = None) -> ToolGroup:
    """Helper function to create a ToolGroup for testing."""
    config = MCPServerConfig(
        name="test_server",
        stdio=StdioConfig(command="test", args=[]),
        namespace_mappings=namespace_mappings,
    )
    return ToolGroup(server_config=config, tools=tools)


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
        expected = 'def plus(x: number, y: number) -> Any:\n    """Add two numbers together"""\n    ...'
        assert result == expected

    def test_builtin_tool(self):
        """Test builtin tool (with builtins_ prefix)."""
        tool = Tool(
            name="builtins_print",
            func=None,
            description="Print text to output",
            parameters=[ToolParameter(name="text", type="string")],
        )
        result = _format_function_description(tool)
        expected = 'def print(text: string) -> Any:\n    """Print text to output"""\n    ...'
        assert result == expected

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
        expected = 'def liquid_template_as_str(template: string, data: string) -> Any:\n    """Render a liquid template"""\n    ...'
        assert result == expected

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
        expected = 'def func(arg1, arg2) -> Any:\n    """Helper function"""\n    ...'
        assert result == expected

    def test_tool_no_parameters(self):
        """Test tool with no parameters."""
        tool = Tool(
            name="utils_get_version",
            func=None,
            description="Get current version",
            parameters=None,
        )
        result = _format_function_description(tool)
        expected = 'def version() -> Any:\n    """Get current version"""\n    ...'
        assert result == expected

    def test_tool_with_return_type_annotation(self):
        """Test tool with function that has return type annotation."""
        def sample_func(x: int, y: int) -> int:
            return x + y

        tool = Tool(
            name="math_operations_add",
            func=sample_func,
            description="Add two integers",
            parameters=[
                ToolParameter(name="x", type="int"),
                ToolParameter(name="y", type="int"),
            ],
        )
        result = _format_function_description(tool)
        expected = 'def add(x: int, y: int) -> int:\n    """Add two integers"""\n    ...'
        assert result == expected

    def test_tool_with_none_return_type(self):
        """Test tool with function that returns None."""
        def sample_func(text: str) -> None:
            print(text)

        tool = Tool(
            name="builtins_print",
            func=sample_func,
            description="Print text",
            parameters=[ToolParameter(name="text", type="str")],
        )
        result = _format_function_description(tool)
        expected = 'def print(text: str) -> None:\n    """Print text"""\n    ...'
        assert result == expected


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

        # Without namespace mappings, all tools go under server name
        root = Folder.from_tools([create_tool_group(tools)])

        # Should have test_server folder
        assert len(root.folders) == 1
        test_server_folder = root.folders[0]
        assert test_server_folder.name == "test_server"

        # All tools should be directly under test_server
        assert len(test_server_folder.tools) == 6

    def test_nested_subnamespaces_show_counts(self):
        """Test deeply nested subnamespaces show correct counts with namespace mapping."""
        tools = [
            Tool(name="browser_console_messages_get", func=None, description="Get messages", parameters=None),
            Tool(name="browser_console_errors_get", func=None, description="Get errors", parameters=None),
            Tool(name="browser_console_warnings_get", func=None, description="Get warnings", parameters=None),
            Tool(name="browser_fill_form", func=None, description="Fill form", parameters=None),
            Tool(name="browser_fill_input", func=None, description="Fill input", parameters=None),
            Tool(name="browser_fill_select", func=None, description="Fill select", parameters=None),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["browser_console_*"], namespace="browser.console"),
            NamespaceMapping(tools=["browser_fill_*"], namespace="browser.fill"),
        ]

        root = Folder.from_tools([create_tool_group(tools, namespace_mappings)])

        # Check test_server.browser level
        result = browse_tools(root, "test_server.browser")
        assert "Namespaces:" in result
        assert "test_server.browser.console (subnamespaces: 0, functions: 3)" in result
        assert "test_server.browser.fill (subnamespaces: 0, functions: 3)" in result


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

        namespace_mappings = [
            NamespaceMapping(tools=["api_users_*"], namespace="api.users")
        ]

        # Build folder structure using Folder.from_tools
        root = Folder.from_tools([create_tool_group(tools, namespace_mappings)])

        # Navigate to test_server.api.users folder where the tool should be
        result = browse_tools(root, "test_server.api.users")

        # Should NOT show Types section (root schema is already in function params)
        assert "Types:" not in result

        # Should show Functions section
        assert "Functions:" in result
        assert "def create(name: string, email: string) -> Any:" in result
        assert '"""Create a new user"""' in result

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

        namespace_mappings = [
            NamespaceMapping(tools=["api_users_*"], namespace="api.users")
        ]

        # Build folder structure using Folder.from_tools
        root = Folder.from_tools([create_tool_group(tools, namespace_mappings)])

        # Navigate to test_server.api.users folder where the tool should be
        result = browse_tools(root, "test_server.api.users")

        # Should show Types section with the nested TypedDict
        assert "Types:" in result
        assert "class UserDict(TypedDict):" in result
        assert "name: str" in result
        assert "email: str" in result

        # Should also show Functions section
        assert "Functions:" in result
        assert "def create(user: object) -> Any:" in result
        assert '"""Create a new user"""' in result

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

        namespace_mappings = [
            NamespaceMapping(tools=["api_users_*"], namespace="api.users")
        ]

        root = Folder.from_tools([create_tool_group(tools, namespace_mappings)])
        result = browse_tools(root, "test_server.api.users")

        # Should NOT show Types section
        assert "Types:" not in result

        # Should show Functions section
        assert "Functions:" in result
        assert "def get(user_id: string) -> Any:" in result
        assert '"""Get user by ID"""' in result

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

        namespace_mappings = [
            NamespaceMapping(tools=["data_records_*"], namespace="data.records")
        ]

        root = Folder.from_tools([create_tool_group(tools, namespace_mappings)])
        result = browse_tools(root, "test_server.data.records")

        # Should show Types section for array items
        assert "Types:" in result
        assert "class RecordsDict(TypedDict):" in result
        assert "id: int" in result
        assert "value: NotRequired[str]" in result

        # Should show function
        assert "Functions:" in result
        assert "def create(records: list) -> Any:" in result
        assert '"""Create multiple records"""' in result

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

        namespace_mappings = [
            NamespaceMapping(tools=["data_records_*"], namespace="data.records")
        ]

        root = Folder.from_tools([create_tool_group([tool_with_nested, tool_without_nested, tool_extra], namespace_mappings)])
        result = browse_tools(root, "test_server.data.records")

        # Should show Types section only for tool_with_nested
        assert "Types:" in result
        assert "class RecordDict(TypedDict):" in result
        assert "id: int" in result
        assert "value: NotRequired[str]" in result

        # Should show both functions
        assert "Functions:" in result
        assert "def create(record: object) -> Any:" in result
        assert '"""Create record"""' in result
        assert "def delete(id: integer) -> Any:" in result
        assert '"""Delete record"""' in result


class TestNamespaceMappings:
    """Test suite for namespace mapping functionality."""

    def test_simple_prefix_mapping(self):
        """Test basic prefix to namespace mapping with server name prepended."""
        tools = [
            Tool(
                name="mcp__playwright__browser_click",
                func=None,
                description="Click element",
                parameters=None,
            ),
            Tool(
                name="mcp__playwright__browser_navigate",
                func=None,
                description="Navigate to URL",
                parameters=None,
            ),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["mcp__playwright__browser_*"], namespace="browser")
        ]

        tool_group = create_tool_group(tools, namespace_mappings)
        root = Folder.from_tools([tool_group])

        # Should have test_server folder (server name)
        assert len(root.folders) == 1
        assert root.folders[0].name == "test_server"

        # test_server should have browser subfolder
        test_server_folder = root.folders[0]
        assert len(test_server_folder.folders) == 1
        browser_folder = test_server_folder.folders[0]
        assert browser_folder.name == "browser"

        # Browser folder should have 2 tools
        assert len(browser_folder.tools) == 2

        # Original names should be preserved in tools
        tool_names = [t.name for t in browser_folder.tools]
        assert "mcp__playwright__browser_click" in tool_names
        assert "mcp__playwright__browser_navigate" in tool_names

    def test_nested_namespace_mapping(self):
        """Test mapping to nested namespace with dots and server name prepended."""
        tools = [
            Tool(
                name="mcp__playwright__browser_tools_click",
                func=None,
                description="Click element",
                parameters=None,
            ),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["mcp__playwright__browser_tools_*"], namespace="browser.tools")
        ]

        tool_group = create_tool_group(tools, namespace_mappings)
        root = Folder.from_tools([tool_group])

        # Should have test_server folder (server name)
        assert len(root.folders) == 1
        test_server_folder = root.folders[0]
        assert test_server_folder.name == "test_server"

        # test_server should have browser subfolder
        assert len(test_server_folder.folders) == 1
        browser_folder = test_server_folder.folders[0]
        assert browser_folder.name == "browser"

        # Browser should have tools subfolder
        assert len(browser_folder.folders) == 1
        tools_folder = browser_folder.folders[0]
        assert tools_folder.name == "tools"

        # Tools folder should have the click tool
        assert len(tools_folder.tools) == 1
        assert tools_folder.tools[0].name == "mcp__playwright__browser_tools_click"

    def test_multiple_prefix_mappings(self):
        """Test multiple prefix mappings in same config with server name prepended."""
        tools = [
            Tool(name="mcp__playwright__browser_click", func=None, description="", parameters=None),
            Tool(name="mcp__playwright__browser_navigate", func=None, description="", parameters=None),
            Tool(name="mcp__playwright__page_screenshot", func=None, description="", parameters=None),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["mcp__playwright__browser_*"], namespace="browser"),
            NamespaceMapping(tools=["mcp__playwright__page_*"], namespace="page"),
        ]

        tool_group = create_tool_group(tools, namespace_mappings)
        root = Folder.from_tools([tool_group])

        # Should have test_server folder
        assert len(root.folders) == 1
        test_server_folder = root.folders[0]
        assert test_server_folder.name == "test_server"

        # test_server should have browser and page subfolders
        assert len(test_server_folder.folders) == 2
        folder_names = {f.name for f in test_server_folder.folders}
        assert "browser" in folder_names
        assert "page" in folder_names

        # Browser should have 2 tools
        browser_folder = next(f for f in test_server_folder.folders if f.name == "browser")
        assert len(browser_folder.tools) == 2

        # Page should have 1 tool
        page_folder = next(f for f in test_server_folder.folders if f.name == "page")
        assert len(page_folder.tools) == 1

    def test_unmapped_tools_go_under_server_name(self):
        """Test that tools not matching any mapping go under server name."""
        tools = [
            Tool(name="mcp__playwright__browser_click", func=None, description="", parameters=None),
            Tool(name="other_tool_something", func=None, description="", parameters=None),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["mcp__playwright__browser_*"], namespace="browser")
        ]

        tool_group = create_tool_group(tools, namespace_mappings)
        root = Folder.from_tools([tool_group])

        # Should have test_server folder
        assert len(root.folders) == 1
        test_server_folder = root.folders[0]
        assert test_server_folder.name == "test_server"

        # test_server should have browser subfolder
        assert len(test_server_folder.folders) == 1
        browser_folder = test_server_folder.folders[0]
        assert browser_folder.name == "browser"

        # test_server should have the unmapped tool directly
        assert len(test_server_folder.tools) == 1
        assert test_server_folder.tools[0].name == "other_tool_something"

    def test_builtins_always_at_root(self):
        """Test that builtins are always at root regardless of mappings or server name."""
        tools = [
            Tool(name="builtins_print", func=None, description="", parameters=None),
            Tool(name="mcp__playwright__browser_click", func=None, description="", parameters=None),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["mcp__playwright__browser_*"], namespace="browser"),
            # Even if we try to map builtins, they should stay at root
            NamespaceMapping(tools=["builtins_*"], namespace="utils"),
        ]

        tool_group = create_tool_group(tools, namespace_mappings)
        root = Folder.from_tools([tool_group])

        # Builtin should be at root
        assert len(root.tools) == 1
        assert root.tools[0].name == "builtins_print"

        # Should have test_server folder
        assert len(root.folders) == 1
        test_server_folder = root.folders[0]
        assert test_server_folder.name == "test_server"

        # test_server should have browser subfolder
        assert len(test_server_folder.folders) == 1
        assert test_server_folder.folders[0].name == "browser"

    def test_multiple_tool_groups(self):
        """Test combining tools from multiple servers with different mappings."""
        playwright_tools = [
            Tool(name="mcp__playwright__browser_click", func=None, description="", parameters=None),
        ]
        playwright_mappings = [
            NamespaceMapping(tools=["mcp__playwright__browser_*"], namespace="browser")
        ]

        azure_tools = [
            Tool(name="mcp__azure__devops_get_projects", func=None, description="", parameters=None),
        ]
        azure_mappings = [
            NamespaceMapping(tools=["mcp__azure__devops_*"], namespace="azure.devops")
        ]

        # Create tool groups with different server names
        config1 = MCPServerConfig(
            name="playwright",
            stdio=StdioConfig(command="test", args=[]),
            namespace_mappings=playwright_mappings,
        )
        playwright_group = ToolGroup(server_config=config1, tools=playwright_tools)

        config2 = MCPServerConfig(
            name="azure",
            stdio=StdioConfig(command="test", args=[]),
            namespace_mappings=azure_mappings,
        )
        azure_group = ToolGroup(server_config=config2, tools=azure_tools)

        root = Folder.from_tools([playwright_group, azure_group])

        # Should have playwright and azure folders (server names)
        assert len(root.folders) == 2
        folder_names = {f.name for f in root.folders}
        assert "playwright" in folder_names
        assert "azure" in folder_names

        # Playwright should have browser subfolder
        playwright_folder = next(f for f in root.folders if f.name == "playwright")
        assert len(playwright_folder.folders) == 1
        assert playwright_folder.folders[0].name == "browser"

        # Azure should have azure subfolder, then devops subfolder
        azure_folder = next(f for f in root.folders if f.name == "azure")
        assert len(azure_folder.folders) == 1
        azure_sub_folder = azure_folder.folders[0]
        assert azure_sub_folder.name == "azure"
        assert len(azure_sub_folder.folders) == 1
        assert azure_sub_folder.folders[0].name == "devops"

    def test_empty_remaining_name(self):
        """Test when prefix exactly matches tool name (no remaining part) with server name."""
        tools = [
            Tool(name="mcp__playwright__browser", func=None, description="", parameters=None),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["mcp__playwright__*"], namespace="playwright")
        ]

        tool_group = create_tool_group(tools, namespace_mappings)
        root = Folder.from_tools([tool_group])

        # Should have test_server folder
        assert len(root.folders) == 1
        test_server_folder = root.folders[0]
        assert test_server_folder.name == "test_server"

        # test_server should have playwright subfolder
        assert len(test_server_folder.folders) == 1
        playwright_folder = test_server_folder.folders[0]
        assert playwright_folder.name == "playwright"

        # Tool should be in the playwright folder (remaining name was "browser")
        assert len(playwright_folder.tools) == 1

    def test_browse_with_namespace_mapping(self):
        """Test browse_tools output with namespace mappings and server name prefix."""
        tools = [
            Tool(
                name="mcp__playwright__browser_click",
                func=None,
                description="Click on element",
                parameters=[ToolParameter(name="selector", type="string")],
            ),
            Tool(
                name="mcp__playwright__browser_navigate",
                func=None,
                description="Navigate to URL",
                parameters=[ToolParameter(name="url", type="string")],
            ),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["mcp__playwright__browser_*"], namespace="browser")
        ]

        tool_group = create_tool_group(tools, namespace_mappings)
        root = Folder.from_tools([tool_group])

        # Browse root - should show test_server
        result = browse_tools(root, "")
        assert "Namespaces:" in result
        assert "test_server (subnamespaces: 1, functions: 0)" in result

        # Browse test_server namespace - should show browser
        result = browse_tools(root, "test_server")
        assert "Namespaces:" in result
        assert "test_server.browser (subnamespaces: 0, functions: 2)" in result

        # Browse test_server.browser namespace - should show functions
        result = browse_tools(root, "test_server.browser")
        assert "Functions:" in result
        assert "def click(selector: string) -> Any:" in result
        assert '"""Click on element"""' in result
        assert "def navigate(url: string) -> Any:" in result
        assert '"""Navigate to URL"""' in result

    def test_suffix_pattern_mapping(self):
        """Test suffix pattern (*name) for matching tools ending with a suffix."""
        tools = [
            Tool(name="get_user", func=None, description="Get user", parameters=None),
            Tool(name="fetch_user", func=None, description="Fetch user", parameters=None),
            Tool(name="create_product", func=None, description="Create product", parameters=None),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["*_user"], namespace="users")
        ]

        tool_group = create_tool_group(tools, namespace_mappings)
        root = Folder.from_tools([tool_group])

        # Should have test_server folder
        assert len(root.folders) == 1
        test_server_folder = root.folders[0]
        assert test_server_folder.name == "test_server"

        # test_server should have users subfolder
        assert len(test_server_folder.folders) == 1
        users_folder = test_server_folder.folders[0]
        assert users_folder.name == "users"

        # Users folder should have 2 tools (get and fetch)
        assert len(users_folder.tools) == 2
        tool_names = [t.name for t in users_folder.tools]
        assert "get_user" in tool_names
        assert "fetch_user" in tool_names

        # create_product should be directly under test_server
        assert len(test_server_folder.tools) == 1
        assert test_server_folder.tools[0].name == "create_product"

    def test_substring_pattern_mapping(self):
        """Test substring pattern (*name*) for matching tools containing a substring."""
        tools = [
            Tool(name="fetch_user_data", func=None, description="Fetch user data", parameters=None),
            Tool(name="get_user_profile", func=None, description="Get user profile", parameters=None),
            Tool(name="get_product", func=None, description="Get product", parameters=None),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["*user*"], namespace="users")
        ]

        tool_group = create_tool_group(tools, namespace_mappings)
        root = Folder.from_tools([tool_group])

        # Should have test_server folder
        assert len(root.folders) == 1
        test_server_folder = root.folders[0]
        assert test_server_folder.name == "test_server"

        # test_server should have users subfolder
        assert len(test_server_folder.folders) == 1
        users_folder = test_server_folder.folders[0]
        assert users_folder.name == "users"

        # Users folder should have 2 tools (both containing 'user')
        assert len(users_folder.tools) == 2
        tool_names = [t.name for t in users_folder.tools]
        assert "fetch_user_data" in tool_names
        assert "get_user_profile" in tool_names

        # get_product should be directly under test_server
        assert len(test_server_folder.tools) == 1
        assert test_server_folder.tools[0].name == "get_product"

    def test_multiple_patterns_in_one_mapping(self):
        """Test multiple patterns in a single namespace mapping."""
        tools = [
            Tool(name="browser_click", func=None, description="Click", parameters=None),
            Tool(name="browser_navigate", func=None, description="Navigate", parameters=None),
            Tool(name="page_screenshot", func=None, description="Screenshot", parameters=None),
            Tool(name="page_title", func=None, description="Get title", parameters=None),
            Tool(name="network_request", func=None, description="Request", parameters=None),
        ]

        namespace_mappings = [
            # Multiple patterns in one mapping go to the same namespace
            NamespaceMapping(tools=["browser_*", "page_*"], namespace="playwright")
        ]

        tool_group = create_tool_group(tools, namespace_mappings)
        root = Folder.from_tools([tool_group])

        # Should have test_server folder
        assert len(root.folders) == 1
        test_server_folder = root.folders[0]
        assert test_server_folder.name == "test_server"

        # test_server should have playwright subfolder
        assert len(test_server_folder.folders) == 1
        playwright_folder = test_server_folder.folders[0]
        assert playwright_folder.name == "playwright"

        # Playwright folder should have 4 tools (browser_* and page_*)
        assert len(playwright_folder.tools) == 4
        tool_names = [t.name for t in playwright_folder.tools]
        assert "browser_click" in tool_names
        assert "browser_navigate" in tool_names
        assert "page_screenshot" in tool_names
        assert "page_title" in tool_names

        # network_request should be directly under test_server
        assert len(test_server_folder.tools) == 1
        assert test_server_folder.tools[0].name == "network_request"

    def test_pattern_priority_first_match_wins(self):
        """Test that first matching pattern wins when multiple patterns could match."""
        tools = [
            Tool(name="browser_console_log", func=None, description="Log", parameters=None),
        ]

        namespace_mappings = [
            # Both patterns would match, but first should win
            NamespaceMapping(tools=["browser_*", "*_log"], namespace="first"),
            NamespaceMapping(tools=["*console*"], namespace="second"),
        ]

        tool_group = create_tool_group(tools, namespace_mappings)
        root = Folder.from_tools([tool_group])

        # Should have test_server folder
        assert len(root.folders) == 1
        test_server_folder = root.folders[0]

        # test_server should have 'first' subfolder (first pattern matched)
        assert len(test_server_folder.folders) == 1
        first_folder = test_server_folder.folders[0]
        assert first_folder.name == "first"

        # Tool should be in first folder
        assert len(first_folder.tools) == 1
        assert first_folder.tools[0].name == "browser_console_log"

    def test_playwright_namespace_structure_from_switchboard_yaml(self):
        """Test comprehensive playwright namespace structure matching switchboard.yaml config."""
        # Simulate the actual playwright tools (as they come from the MCP server)
        tools = [
            # Navigation & Control
            Tool(name="browser_navigate", func=None, description="Navigate", parameters=None),
            Tool(name="browser_navigate_back", func=None, description="Back", parameters=None),
            Tool(name="browser_close", func=None, description="Close", parameters=None),
            Tool(name="browser_install", func=None, description="Install", parameters=None),
            # Page Interaction
            Tool(name="browser_click", func=None, description="Click", parameters=None),
            Tool(name="browser_hover", func=None, description="Hover", parameters=None),
            Tool(name="browser_drag", func=None, description="Drag", parameters=None),
            Tool(name="browser_type", func=None, description="Type", parameters=None),
            Tool(name="browser_press_key", func=None, description="Press key", parameters=None),
            # Form Handling
            Tool(name="browser_fill_form", func=None, description="Fill form", parameters=None),
            Tool(name="browser_file_upload", func=None, description="Upload", parameters=None),
            Tool(name="browser_select_option", func=None, description="Select", parameters=None),
            # Information Gathering
            Tool(name="browser_snapshot", func=None, description="Snapshot", parameters=None),
            Tool(name="browser_take_screenshot", func=None, description="Screenshot", parameters=None),
            Tool(name="browser_console_messages", func=None, description="Console", parameters=None),
            Tool(name="browser_network_requests", func=None, description="Network", parameters=None),
            # Window & Dialog Management
            Tool(name="browser_resize", func=None, description="Resize", parameters=None),
            Tool(name="browser_tabs", func=None, description="Tabs", parameters=None),
            Tool(name="browser_handle_dialog", func=None, description="Dialog", parameters=None),
            # Advanced
            Tool(name="browser_evaluate", func=None, description="Evaluate", parameters=None),
            Tool(name="browser_run_code", func=None, description="Code", parameters=None),
            Tool(name="browser_wait_for", func=None, description="Wait", parameters=None),
        ]

        # Namespace mappings matching switchboard.yaml
        namespace_mappings = [
            NamespaceMapping(
                namespace="navigation",
                tools=[
                    "browser_navigate*",
                    "browser_navigate_back",
                    "browser_close",
                    "browser_install",
                ]
            ),
            NamespaceMapping(
                namespace="interaction",
                tools=[
                    "browser_click",
                    "browser_hover",
                    "browser_drag",
                    "browser_type",
                    "browser_press_key",
                ]
            ),
            NamespaceMapping(
                namespace="forms",
                tools=[
                    "browser_fill_form",
                    "browser_file_upload",
                    "browser_select_option",
                ]
            ),
            NamespaceMapping(
                namespace="inspection",
                tools=[
                    "browser_snapshot",
                    "browser_take_screenshot",
                    "browser_console_messages",
                    "browser_network_requests",
                ]
            ),
            NamespaceMapping(
                namespace="windows",
                tools=[
                    "browser_resize",
                    "browser_tabs",
                    "browser_handle_dialog",
                ]
            ),
            NamespaceMapping(
                namespace="advanced",
                tools=[
                    "browser_evaluate",
                    "browser_run_code",
                    "browser_wait_for",
                ]
            ),
        ]

        # Create tool group with "playwright" server name to match switchboard.yaml
        config = MCPServerConfig(
            name="playwright",
            stdio=StdioConfig(command="npx", args=["@playwright/mcp@latest"]),
            namespace_mappings=namespace_mappings,
            remove_prefix="browser_",  # Match switchboard.yaml
        )
        tool_group = ToolGroup(server_config=config, tools=tools)
        root = Folder.from_tools([tool_group])

        # Should have playwright folder at root
        assert len(root.folders) == 1
        playwright_folder = root.folders[0]
        assert playwright_folder.name == "playwright"

        # Should have 6 namespace subfolders
        assert len(playwright_folder.folders) == 6
        namespace_names = {f.name for f in playwright_folder.folders}
        assert namespace_names == {"navigation", "interaction", "forms", "inspection", "windows", "advanced"}

        # Verify each namespace has the correct tools with PREFIX REMOVED
        navigation_folder = next(f for f in playwright_folder.folders if f.name == "navigation")
        assert len(navigation_folder.tools) == 4
        nav_tool_names = {t.name for t in navigation_folder.tools}
        # After prefix removal: mcp__playwright__browser_navigate -> navigate
        assert "navigate" in nav_tool_names
        assert "navigate_back" in nav_tool_names
        assert "close" in nav_tool_names
        assert "install" in nav_tool_names

        interaction_folder = next(f for f in playwright_folder.folders if f.name == "interaction")
        assert len(interaction_folder.tools) == 5

        forms_folder = next(f for f in playwright_folder.folders if f.name == "forms")
        assert len(forms_folder.tools) == 3

        inspection_folder = next(f for f in playwright_folder.folders if f.name == "inspection")
        assert len(inspection_folder.tools) == 4

        windows_folder = next(f for f in playwright_folder.folders if f.name == "windows")
        assert len(windows_folder.tools) == 3

        advanced_folder = next(f for f in playwright_folder.folders if f.name == "advanced")
        assert len(advanced_folder.tools) == 3

        # Test browsing the structure
        result = browse_tools(root, "playwright")
        assert "Namespaces:" in result
        assert "playwright.navigation" in result
        assert "playwright.interaction" in result
        assert "playwright.forms" in result
        assert "playwright.inspection" in result
        assert "playwright.windows" in result
        assert "playwright.advanced" in result

        # Test browsing a specific namespace shows tools with shortened names
        result = browse_tools(root, "playwright.navigation")
        assert "Functions:" in result
        # With remove_prefix, tools should have clean names
        assert "navigate" in result.lower()
        # Should NOT have the prefixed name (browser_ prefix should be removed)
        assert "browser_navigate" not in result

    def test_remove_prefix_configuration(self):
        """Test that remove_prefix configuration strips prefix from tool names."""
        tools = [
            Tool(name="mcp__playwright__browser_click", func=None, description="Click", parameters=None),
            Tool(name="mcp__playwright__browser_navigate", func=None, description="Navigate", parameters=None),
            Tool(name="mcp__playwright__browser_type", func=None, description="Type", parameters=None),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["mcp__playwright__browser_*"], namespace="browser")
        ]

        # Create config with remove_prefix
        config = MCPServerConfig(
            name="playwright",
            stdio=StdioConfig(command="test", args=[]),
            namespace_mappings=namespace_mappings,
            remove_prefix="mcp__playwright__browser_",
        )
        tool_group = ToolGroup(server_config=config, tools=tools)
        root = Folder.from_tools([tool_group])

        # Should have playwright folder
        assert len(root.folders) == 1
        playwright_folder = root.folders[0]
        assert playwright_folder.name == "playwright"

        # Should have browser subfolder
        assert len(playwright_folder.folders) == 1
        browser_folder = playwright_folder.folders[0]
        assert browser_folder.name == "browser"

        # Tools should have prefix removed
        assert len(browser_folder.tools) == 3
        tool_names = {t.name for t in browser_folder.tools}
        assert tool_names == {"click", "navigate", "type"}

        # Verify original names are NOT in the tools
        assert "mcp__playwright__browser_click" not in tool_names

    def test_remove_prefix_only_matching_tools(self):
        """Test that remove_prefix only affects tools that start with the prefix."""
        tools = [
            Tool(name="mcp__playwright__browser_click", func=None, description="Click", parameters=None),
            Tool(name="other_tool", func=None, description="Other", parameters=None),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["mcp__playwright__browser_*"], namespace="browser")
        ]

        config = MCPServerConfig(
            name="playwright",
            stdio=StdioConfig(command="test", args=[]),
            namespace_mappings=namespace_mappings,
            remove_prefix="mcp__playwright__browser_",
        )
        tool_group = ToolGroup(server_config=config, tools=tools)
        root = Folder.from_tools([tool_group])

        playwright_folder = root.folders[0]
        browser_folder = playwright_folder.folders[0]

        # Tool with prefix should have it removed
        browser_tool_names = {t.name for t in browser_folder.tools}
        assert "click" in browser_tool_names
        assert "mcp__playwright__browser_click" not in browser_tool_names

        # Tool without prefix should keep its original name
        assert len(playwright_folder.tools) == 1
        assert playwright_folder.tools[0].name == "other_tool"

    def test_no_remove_prefix_preserves_names(self):
        """Test that without remove_prefix, tool names are preserved."""
        tools = [
            Tool(name="mcp__playwright__browser_click", func=None, description="Click", parameters=None),
        ]

        namespace_mappings = [
            NamespaceMapping(tools=["mcp__playwright__browser_*"], namespace="browser")
        ]

        config = MCPServerConfig(
            name="playwright",
            stdio=StdioConfig(command="test", args=[]),
            namespace_mappings=namespace_mappings,
            # No remove_prefix configured
        )
        tool_group = ToolGroup(server_config=config, tools=tools)
        root = Folder.from_tools([tool_group])

        playwright_folder = root.folders[0]
        browser_folder = playwright_folder.folders[0]

        # Tool should keep full name
        assert len(browser_folder.tools) == 1
        assert browser_folder.tools[0].name == "mcp__playwright__browser_click"
