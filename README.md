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
