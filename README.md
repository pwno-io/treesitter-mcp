# Tree-sitter MCP Server

A Model Context Protocol (MCP) server for code analysis using Tree-sitter. This tool provides capabilities to parse code, extract symbols, generate call graphs, find usages, and run custom queries against code in 10 programming languages.

## Features

-   **AST Retrieval**: Get the full Abstract Syntax Tree (AST) of a file.
-   **Symbol Extraction**: Find function and variable definitions.
-   **Call Graph**: Generate function call graphs.
-   **Tree-sitter Queries**: Run custom S-expression queries against your code.
-   **Usage Finder**: Find usages of functions and variables.
-   **Dependency Extraction**: List file dependencies (includes/imports).
-   **Multi-Language Support**: Currently supports C, C++, Python, JavaScript, TypeScript, Go, Java, PHP, Rust, and Ruby.

## Installation

### Prerequisites

-   Python 3.10+
-   `pip`

### Setup

1.  Clone the repository.
2.  Install the package:
    ```bash
    # Using uv (recommended)
    uv pip install -e .
    
    # Or using pip
    pip install -e .
    ```

This will install the `treesitter-mcp` command-line tool.

You can also run it directly without installation using `uvx`:
```bash
uvx treesitter-mcp
```

## Usage

### MCP Server (Default)

By default, `treesitter-mcp` runs as an MCP server in stdio mode:

```bash
treesitter-mcp
```

This is perfect for integrating with MCP clients like Claude Desktop. See `docs/MCP_USAGE.md` for configuration instructions.

### HTTP Mode

To run the server in HTTP mode for testing or development:

```bash
treesitter-mcp --http --port 8000 --host 127.0.0.1
```

#### Selecting Specific Tools

You can limit which tools are exposed by using the `--tools` argument. This is useful when you only need specific functionality:

```bash
# Expose only specific tools
treesitter-mcp --http --port 8000 --tools treesitter_analyze_file,treesitter_get_ast

# URL-based selection (e.g., for MCP clients)
# http://127.0.0.1:8000?tools=treesitter_analyze_file,treesitter_get_ast
```

Available tool names:
- `treesitter_analyze_file` - Analyze files and extract symbols
- `treesitter_get_call_graph` - Generate function call graphs
- `treesitter_find_function` - Search for function definitions
- `treesitter_find_variable` - Search for variable declarations and usages
- `treesitter_get_supported_languages` - List supported languages
- `treesitter_get_ast` - Get the complete Abstract Syntax Tree
- `treesitter_get_node_at_point` - Get AST node at a specific point
- `treesitter_get_node_for_range` - Get AST node for a range
- `treesitter_cursor_walk` - Cursor-style view with context
- `treesitter_run_query` - Run custom Tree-sitter queries
- `treesitter_find_usage` - Find all usages of a symbol
- `treesitter_get_dependencies` - Extract file dependencies

If `--tools` is not provided, all tools are exposed by default.

### Example with uvx

```bash
# Run in stdio mode (default)
uvx treesitter-mcp

# Run in HTTP mode
uvx treesitter-mcp --http --port 8000

Configure your MCP client (e.g., Claude Desktop) to use this server. See `docs/MCP_USAGE.md` for detailed configuration instructions.

## Supported Languages

### Language Feature Matrix

| Language | analyze_file | get_ast | get_call_graph | find_function | find_variable | find_usage | get_dependencies |
|----------|--------------|---------|----------------|---------------|---------------|------------|------------------|
| C        | ✅           | ✅      | ✅             | ✅            | ✅            | ✅         | ✅               |
| C++      | ✅           | ✅      | ✅             | ✅            | ✅            | ✅         | ✅               |
| Python   | ✅           | ✅      | ✅             | ✅            | ✅            | ✅         | ✅               |
| JavaScript | ✅         | ✅      | ✅             | ✅            | ✅            | ✅         | ✅               |
| TypeScript| ✅         | ✅      | ✅             | ✅            | ✅            | ✅         | ✅               |
| Go       | ✅           | ✅      | ✅             | ✅            | ✅            | ✅         | ✅               |
| Java     | ✅           | ✅      | ✅             | ✅            | ✅            | ✅         | ✅               |
| PHP      | ✅           | ✅      | ✅             | ✅            | ✅            | ✅         | ✅               |
| Rust     | ✅           | ✅      | ✅             | ✅            | ✅            | ✅         | ✅               |
| Ruby     | ✅           | ✅      | ✅             | ✅            | ✅            | ✅         | ✅               |

### Supported File Extensions

| Language | Extensions |
|----------|------------|
| C        | `.c` |
| C++      | `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp` |
| Python   | `.py` |
| JavaScript | `.js`, `.jsx`, `.mjs`, `.cjs` |
| TypeScript | `.ts`, `.tsx`, `.cts`, `.mts` |
| Go       | `.go` |
| Java     | `.java` |
| PHP      | `.php`, `.phtml` |
| Rust     | `.rs` |
| Ruby     | `.rb` |

## Documentation

See the `docs/` directory for more details:
-   [API Reference](docs/API.md)
-   [MCP Server Usage](docs/MCP_USAGE.md)
-   [Architecture](docs/ARCHITECTURE.md)
