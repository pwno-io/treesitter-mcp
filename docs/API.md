# API Reference

## CLI Arguments

The CLI (`src/treesitter_mcp/cli.py`) supports the following arguments:

| Argument | Description | Example |
| :--- | :--- | :--- |
| `file` | Path to the file to analyze (Required). | `test.c` |
| `--ast` | Output the full Abstract Syntax Tree (AST) in JSON. | `--ast` |
| `--find-function <name>` | Find the definition of a function by name. | `--find-function main` |
| `--find-variable <name>` | Find the definition and usage of a variable by name. | `--find-variable count` |
| `--find-usage <name>` | Find all usages (and definitions) of a symbol. | `--find-usage helper` |
| `--dependencies` | List file dependencies (includes/imports). | `--dependencies` |
| `--call-graph` | Generate a call graph for the file (C/C++/JavaScript/PHP/Rust/TypeScript/Go/Java). | `--call-graph` |
| `--query <query>` | Run a custom Tree-sitter S-expression query. | `--query "(identifier) @id"` |

## MCP Tools

The MCP server (`src/treesitter_mcp/server.py`) exposes the following tools:

### `get_ast`
Returns the Abstract Syntax Tree of a file.
- **Arguments**: `file_path` (string)
- **Returns**: JSON string of the AST.

### `get_node_at_point`
Returns the smallest AST node covering a specific point.
- **Arguments**: `file_path` (string), `row` (int), `column` (int), `max_depth` (int, optional; default 0)
- **Returns**: JSON AST node (includes field names).

### `get_node_for_range`
Returns the smallest AST node covering a point range.
- **Arguments**: `file_path` (string), `start_row` (int), `start_column` (int), `end_row` (int), `end_column` (int), `max_depth` (int, optional; default 0)
- **Returns**: JSON AST node (includes field names).

### `cursor_walk`
Returns a cursor-style snapshot (focus node + ancestors/siblings/children) at a point.
- **Arguments**: `file_path` (string), `row` (int), `column` (int), `max_depth` (int, optional; default 1)
- **Returns**: JSON object with `focus`, `ancestors`, `siblings`, and `children`.

### `run_query`
Executes a Tree-sitter query against a file.
- **Arguments**:
    - `query` (string): The S-expression query.
    - `file_path` (string): Path to the file.
    - `language` (string, optional): Language override.
- **Returns**: JSON string of captures.

### `find_usage`
Finds usages of a symbol.
- **Arguments**:
    - `name` (string): Symbol name.
    - `file_path` (string): Path to the file.
- **Returns**: JSON string of search results.

### `get_dependencies`
Gets file dependencies.
- **Arguments**: `file_path` (string)
- **Returns**: JSON list of dependency strings.

### `analyze_file`
Performs a default analysis (symbols extraction).
- **Arguments**: `file_path` (string)
- **Returns**: JSON string of analysis results.

### `get_call_graph`
Generates a call graph.
- **Arguments**: `file_path` (string)
- **Returns**: JSON string of the call graph.

### `find_function`
Finds a function definition.
- **Arguments**:
    - `name` (string): Function name.
    - `file_path` (string): Path to the file.
- **Returns**: JSON string of search results.

### `find_variable`
Finds a variable.
- **Arguments**:
    - `name` (string): Variable name.
    - `file_path` (string): Path to the file.
- **Returns**: JSON string of search results.
