# MCP Server Usage

This project implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), allowing AI agents (like Claude) to interact with your code analysis tools.

## Transport

The server uses **stdio** transport by default. This means it communicates via standard input and output.

## Configuration

### Installation

You can install the package using `uv` or run it directly with `uvx`:

```bash
# Install in your environment
cd /path/to/treesitter-mcp
uv pip install -e .

# Or run directly without installation (recommended)
uvx treesitter-mcp
```

### Claude Desktop

Add the following to your `claude_desktop_config.json` (usually located at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

**Recommended (using uvx):**
```json
{
  "mcpServers": {
    "treesitter-mcp": {
      "command": "uvx",
      "args": ["treesitter-mcp"]
    }
  }
}
```

**Alternative (if installed in a virtual environment):**
```json
{
  "mcpServers": {
    "treesitter-mcp": {
      "command": "/path/to/.venv/bin/treesitter-mcp"
    }
  }
}
```

### Generic Agent Configuration

If you are configuring a generic agent, the invocation command is:

```bash
treesitter-mcp
```

The agent should communicate with this process via `stdin`/`stdout` using the JSON-RPC 2.0 protocol defined by MCP.

### HTTP Mode (Optional)

For testing or development, you can run the server in HTTP mode:

```bash
treesitter-mcp --http --port 8000 --host 127.0.0.1
```

## Available Tools for Agents

When connected, the agent will have access to the following tools:

1.  **`treesitter_get_ast(file_path: str, max_depth: int = -1)`**:
    -   *Agent Usage*: "Get the AST for `src/main.c` to understand its structure."
    -   *Returns*: A JSON representation of the syntax tree.

2.  **`treesitter_run_query(query: str, file_path: str, language: str = None)`**:
    -   *Agent Usage*: "Find all function definitions in `src/main.c` using a tree-sitter query."
    -   *Returns*: List of captured nodes and text.

3.  **`treesitter_find_usage(name: str, file_path: str, language: str = None)`**:
    -   *Agent Usage*: "Where is `helper_function` used in `src/main.c`?"
    -   *Returns*: Locations of definitions and usages.

4.  **`treesitter_get_dependencies(file_path: str)`**:
    -   *Agent Usage*: "What files does `src/main.c` include?"
    -   *Returns*: List of header files or imports.

5.  **`treesitter_analyze_file(file_path: str)`**:
    -   *Agent Usage*: "Give me a summary of symbols in `src/main.c`."
    -   *Returns*: List of functions, classes, and variables.

6.  **`treesitter_get_call_graph(file_path: str)`**:
    -   *Agent Usage*: "Show me the call graph for `src/main.c`."
    -   *Returns*: A graph of function calls.

7.  **`treesitter_find_function(file_path: str, name: str)`**:
    -   *Agent Usage*: "Find the function `main` in `src/main.c`."
    -   *Returns*: Symbol information for the function.

8.  **`treesitter_find_variable(file_path: str, name: str)`**:
    -   *Agent Usage*: "Find the variable `counter` in `src/main.c`."
    -   *Returns*: Symbol information for the variable.

9.  **`treesitter_get_supported_languages()`**:
    -   *Agent Usage*: "What languages are supported?"
    -   *Returns*: List of supported languages.

10. **`treesitter_get_node_at_point(file_path: str, row: int, column: int, max_depth: int = 0)`**:
    -   *Agent Usage*: "Get the AST node at line 10, column 5 in `src/main.c`."
    -   *Returns*: AST node at the specified location.

11. **`treesitter_get_node_for_range(file_path: str, start_row: int, start_column: int, end_row: int, end_column: int, max_depth: int = 0)`**:
    -   *Agent Usage*: "Get the AST node covering lines 10-20 in `src/main.c`."
    -   *Returns*: Smallest AST node covering the range.

12. **`treesitter_cursor_walk(file_path: str, row: int, column: int, max_depth: int = 1)`**:
    -   *Agent Usage*: "Get a cursor view at line 10, column 5 in `src/main.c`."
    -   *Returns*: Cursor-style view with focus node and context.

## Example Agent Workflow

1.  **User**: "Analyze `test.c` and tell me what `main` calls."
2.  **Agent**: Calls `treesitter_get_call_graph(file_path="test.c")`.
3.  **Server**: Returns JSON call graph.
4.  **Agent**: Interprets JSON and answers: "`main` calls `helper` and `printf`."
