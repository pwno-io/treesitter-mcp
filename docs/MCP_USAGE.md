# MCP Server Usage

This project implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), allowing AI agents (like Claude) to interact with your code analysis tools.

## Transport

The server uses **stdio** transport. This means it communicates via standard input and output.

## Configuration

### Installation

First, install the package:
```bash
cd /path/to/code-analysis
uv pip install -e .
```

This installs the `code-analysis-server` command globally (in your Python environment).

### Claude Desktop

Add the following to your `claude_desktop_config.json` (usually located at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "code-analysis": {
      "command": "code-analysis-server"
    }
  }
}
```

**Note:** If you installed in a virtual environment, use the full path to the command:
```json
{
  "mcpServers": {
    "code-analysis": {
      "command": "/path/to/.venv/bin/code-analysis-server"
    }
  }
}
```

### Generic Agent Configuration

If you are configuring a generic agent, the invocation command is:

```bash
code-analysis-server
```

The agent should communicate with this process via `stdin`/`stdout` using the JSON-RPC 2.0 protocol defined by MCP.

## Available Tools for Agents

When connected, the agent will have access to the following tools:

1.  **`get_ast(file_path: str)`**:
    -   *Agent Usage*: "Get the AST for `src/main.c` to understand its structure."
    -   *Returns*: A JSON representation of the syntax tree.

2.  **`run_query(query: str, file_path: str, language: str = None)`**:
    -   *Agent Usage*: "Find all function definitions in `src/main.c` using a tree-sitter query."
    -   *Returns*: List of captured nodes and text.

3.  **`find_usage(name: str, file_path: str)`**:
    -   *Agent Usage*: "Where is `helper_function` used in `src/main.c`?"
    -   *Returns*: Locations of definitions and usages.

4.  **`get_dependencies(file_path: str)`**:
    -   *Agent Usage*: "What files does `src/main.c` include?"
    -   *Returns*: List of header files or imports.

5.  **`analyze_file(file_path: str)`**:
    -   *Agent Usage*: "Give me a summary of symbols in `src/main.c`."
    -   *Returns*: List of functions, classes, and variables.

6.  **`get_call_graph(file_path: str)`**:
    -   *Agent Usage*: "Show me the call graph for `src/main.c`."
    -   *Returns*: A graph of function calls.

## Example Agent Workflow

1.  **User**: "Analyze `test.c` and tell me what `main` calls."
2.  **Agent**: Calls `get_call_graph(file_path="test.c")`.
3.  **Server**: Returns JSON call graph.
4.  **Agent**: Interprets JSON and answers: "`main` calls `helper` and `printf`."
