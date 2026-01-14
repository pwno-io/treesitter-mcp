# API Reference

## Common Parameters

All MCP tools accept an optional `output_file` parameter:

| Parameter | Type | Description |
|-----------|------|-------------|
| `output_file` | string (optional) | If provided, writes the result to this file path instead of returning. Returns `{"status": "written", "output_file": "...", "bytes_written": N}` on success. |

## CLI Arguments

The `ts-cli` command (`src/treesitter_mcp/cli/ts_cli.py`) supports the following arguments:

| Argument | Description | Example |
| :--- | :--- | :--- |
| `file` | Path to the file to analyze (required unless `--supported-languages`). | `test.c` |
| `--ast` | Output the full Abstract Syntax Tree (AST) in JSON. | `--ast --max-depth 2` |
| `--call-graph` | Generate a call graph for the file. | `--call-graph` |
| `--find-function <name>` | Find the definition of a function by name. | `--find-function main` |
| `--find-variable <name>` | Find the definition and usage of a variable by name. | `--find-variable count` |
| `--find-usage <name>` | Find all usages (and definitions) of a symbol. | `--find-usage helper` |
| `--dependencies` | List file dependencies (includes/imports). | `--dependencies` |
| `--query <query>` | Run a custom Tree-sitter S-expression query. | `--query "(identifier) @id"` |
| `--source-range <start_row start_col end_row end_col>` | Extract source code for a range. | `--source-range 10 0 12 5` |
| `--node-at-point <row col>` | Get the AST node at a point. | `--node-at-point 5 10` |
| `--node-for-range <start_row start_col end_row end_col>` | Get the AST node for a range. | `--node-for-range 2 0 4 3` |
| `--cursor-walk <row col>` | Get a cursor-style view at a point. | `--cursor-walk 4 12` |
| `--supported-languages` | List supported languages. | `--supported-languages` |
| `--max-depth <n>` | Limit AST/node/cursor depth. | `--ast --max-depth 2` |
| `--include-source` | Include source for find-function/variable. | `--find-function main --include-source` |
| `--language <lang>` | Override language for query/find-usage. | `--query "(identifier) @id" --language javascript` |
| `--output-file <path>` | Write results to a JSON file. | `--output-file out.json` |

## MCP Tools

The MCP server (`src/treesitter_mcp/server.py`) exposes the following tools:

### `get_ast`
Returns the Abstract Syntax Tree of a file.
- **Arguments**: `file_path` (string), `max_depth` (int, optional; default -1), `output_file` (string, optional)
- **Returns**: JSON string of the AST.

### `get_node_at_point`
Returns the smallest AST node covering a specific point.
- **Arguments**: `file_path` (string), `row` (int), `column` (int), `max_depth` (int, optional; default 0), `output_file` (string, optional)
- **Returns**: JSON AST node (includes field names).

### `get_node_for_range`
Returns the smallest AST node covering a point range.
- **Arguments**: `file_path` (string), `start_row` (int), `start_column` (int), `end_row` (int), `end_column` (int), `max_depth` (int, optional; default 0), `output_file` (string, optional)
- **Returns**: JSON AST node (includes field names).

### `cursor_walk`
Returns a cursor-style snapshot (focus node + ancestors/siblings/children) at a point.
- **Arguments**: `file_path` (string), `row` (int), `column` (int), `max_depth` (int, optional; default 1), `output_file` (string, optional)
- **Returns**: JSON object with `focus`, `ancestors`, `siblings`, and `children`.

### `run_query`
Executes a Tree-sitter query against a file.
- **Arguments**:
    - `query` (string): The S-expression query.
    - `file_path` (string): Path to the file.
    - `language` (string, optional): Language override.
    - `output_file` (string, optional)
- **Returns**: JSON string of captures.

### `find_usage`
Finds usages of a symbol.
- **Arguments**:
    - `name` (string): Symbol name.
    - `file_path` (string): Path to the file.
    - `language` (string, optional): Language override.
    - `output_file` (string, optional)
- **Returns**: JSON string of search results.

### `get_dependencies`
Gets file dependencies.
- **Arguments**: `file_path` (string), `output_file` (string, optional)
- **Returns**: JSON list of dependency strings.

### `analyze_file`
Performs a default analysis (symbols extraction).
- **Arguments**: `file_path` (string), `output_file` (string, optional)
- **Returns**: JSON string of analysis results.

### `get_call_graph`
Generates a call graph.
- **Arguments**: `file_path` (string), `output_file` (string, optional)
- **Returns**: JSON string of the call graph.

### `find_function`
Finds a function definition.
- **Arguments**:
    - `file_path` (string): Path to the file.
    - `name` (string): Function name.
    - `include_source` (bool, optional): If true, includes source code for each match.
    - `output_file` (string, optional)
- **Returns**: JSON string of search results.

### `find_variable`
Finds a variable.
- **Arguments**:
    - `file_path` (string): Path to the file.
    - `name` (string): Variable name.
    - `include_source` (bool, optional): If true, includes source code for each match.
    - `output_file` (string, optional)
- **Returns**: JSON string of search results.

### `get_source_for_range`
Extracts source code for a specific line/column range.
- **Arguments**:
    - `file_path` (string): Path to the file.
    - `start_row` (int): Starting line number (0-based).
    - `start_column` (int): Starting column number (0-based).
    - `end_row` (int): Ending line number (0-based).
    - `end_column` (int): Ending column number (0-based).
    - `output_file` (string, optional)
- **Returns**: JSON object with `file_path`, `range`, and `source` fields containing the extracted code text.

### `get_supported_languages`
Lists supported programming languages.
- **Arguments**: `output_file` (string, optional)
- **Returns**: List of language names (e.g., ['python', 'c', 'cpp']).
