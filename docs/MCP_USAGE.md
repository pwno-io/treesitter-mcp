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

### Common Parameter: `output_file`

All tools support an optional `output_file` parameter. When provided, the tool writes its result directly to the specified file (as pretty-printed JSON) instead of returning it to the agent. This prevents context overload for large outputs.

Example usage:
```python
# Returns minimal confirmation, writes full result to file
treesitter_get_ast(file_path="large_file.py", output_file="~/output/ast.json")
# Returns: {"status": "written", "output_file": "/home/user/output/ast.json", "bytes_written": 123456}
```

 1.  **`treesitter_get_ast(file_path: str, max_depth: int = -1, output_file: str = None)`**:
     -   *Agent Usage*: "Get the AST for `src/main.c` to understand its structure."
     -   *Returns*: A JSON representation of the syntax tree.

 2.  **`treesitter_run_query(query: str, file_path: str, language: str = None, output_file: str = None)`**:
     -   *Agent Usage*: "Find all function definitions in `src/main.c` using a tree-sitter query."
     -   *Returns*: List of captured nodes and text.

 3.  **`treesitter_find_usage(name: str, file_path: str, language: str = None, output_file: str = None)`**:
     -   *Agent Usage*: "Where is `helper_function` used in `src/main.c`?"
     -   *Returns*: Locations of definitions and usages.

 4.  **`treesitter_get_dependencies(file_path: str, output_file: str = None)`**:
     -   *Agent Usage*: "What files does `src/main.c` include?"
     -   *Returns*: List of header files or imports.

 5.  **`treesitter_analyze_file(file_path: str, output_file: str = None)`**:
     -   *Agent Usage*: "Give me a summary of symbols in `src/main.c`."
     -   *Returns*: List of functions, classes, and variables.

 6.  **`treesitter_get_call_graph(file_path: str, output_file: str = None)`**:
     -   *Agent Usage*: "Show me the call graph for `src/main.c`."
     -   *Returns*: A graph of function calls.

 7.  **`treesitter_find_function(file_path: str, name: str, include_source: bool = False, output_file: str = None)`**:
     -   *Agent Usage*: "Find the function `main` in `src/main.c`."
     -   *Returns*: Symbol information for the function. If `include_source=True`, includes source code.

 8.  **`treesitter_find_variable(file_path: str, name: str, include_source: bool = False, output_file: str = None)`**:
     -   *Agent Usage*: "Find the variable `counter` in `src/main.c`."
     -   *Returns*: Symbol information for the variable. If `include_source=True`, includes source code.

 9.  **`treesitter_get_supported_languages(output_file: str = None)`**:
     -   *Agent Usage*: "What languages are supported?"
     -   *Returns*: List of supported languages.

 10. **`treesitter_get_node_at_point(file_path: str, row: int, column: int, max_depth: int = 0, output_file: str = None)`**:
     -   *Agent Usage*: "Get the AST node at line 10, column 5 in `src/main.c`."
     -   *Returns*: AST node at the specified location.

 11. **`treesitter_get_node_for_range(file_path: str, start_row: int, start_column: int, end_row: int, end_column: int, max_depth: int = 0, output_file: str = None)`**:
     -   *Agent Usage*: "Get the AST node covering lines 10-20 in `src/main.c`."
     -   *Returns*: Smallest AST node covering the range.

  12. **`treesitter_cursor_walk(file_path: str, row: int, column: int, max_depth: int = 1, output_file: str = None)`**:
      - *Agent Usage*: "Get a cursor view at line 10, column 5 in `src/main.c`."
      - *Returns*: Cursor-style view with focus node and context.

  13. **`treesitter_get_source_for_range(file_path: str, start_row: int, start_column: int, end_row: int, end_column: int, output_file: str = None)`**:
      - *Agent Usage*: "Get the source code for the function at lines 5-15 in `src/main.c`."
      - *Returns*: The actual source code text for the specified range.

## Example Agent Workflow

1.  **User**: "Analyze `test.c` and tell me what `main` calls."
2.  **Agent**: Calls `treesitter_get_call_graph(file_path="test.c")`.
3.  **Server**: Returns JSON call graph.
4.  **Agent**: Interprets JSON and answers: "`main` calls `helper` and `printf`."

## Example: Getting Symbol Source Code

The `treesitter_get_source_for_range` tool allows agents to extract actual source code for symbols they discover. This is useful for providing complete code context in reports.

1.  **User**: "Show me the implementation of the `factorial` function in `test.py`."
2.  **Agent**: First, finds the function:
    ```python
    treesitter_find_function(file_path="test.py", name="factorial")
    ```
3.  **Server**: Returns the function's location:
    ```json
    {
      "matches": [{
        "name": "factorial",
        "kind": "function",
        "location": {
          "start": {"row": 7, "column": 0},
          "end": {"row": 11, "column": 28}
        },
        "file_path": "test.py"
      }]
    }
    ```
4.  **Agent**: Extracts the source code using the location:
    ```python
    treesitter_get_source_for_range(
      file_path="test.py",
      start_row=7, start_column=0,
      end_row=11, end_column=28
    )
    ```
5.  **Server**: Returns the actual source code:
    ```json
    {
      "file_path": "test.py",
      "range": {
        "start": {"row": 7, "column": 0},
        "end": {"row": 11, "column": 28}
      },
      "source": "def factorial(n: int) -> int:\n    \"\"\"Calculate factorial of n.\"\"\"\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n"
    }
    ```
6.  **Agent**: Formats the response:
    ```
    Found function `factorial` at test.py:8-12

    def factorial(n: int) -> int:
        """Calculate factorial of n."""
        if n <= 1:
            return 1
        return n * factorial(n - 1)
    ```
