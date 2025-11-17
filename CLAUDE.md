# Switchboard MCP - Project Guidelines

## Testing
- Never write custom scripts to test code - always write proper unit tests instead
- Use `uv run pytest` for running tests
- Tests are located in the `test/` directory
- Example: `uv run pytest test/test_utils.py -v`
