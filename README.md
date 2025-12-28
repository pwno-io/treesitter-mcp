# Tree-sitter MCP Server

A Model Context Protocol (MCP) server for code analysis using Tree-sitter. This tool provides capabilities to parse code, extract symbols, generate call graphs, find usages, and run custom queries against C, C++, JavaScript, PHP, Rust, TypeScript, Go, Java, and Python code.

## Features

-   **AST Retrieval**: Get the full Abstract Syntax Tree (AST) of a file.
-   **Symbol Extraction**: Find function and variable definitions.
-   **Call Graph**: Generate a call graph for C/C++ functions.
-   **Tree-sitter Queries**: Run custom S-expression queries against your code.
-   **Usage Finder**: Find usages of functions and variables.
-   **Dependency Extraction**: List file dependencies (includes/imports).
-   **Multi-Language Support**: Currently supports C, C++, JavaScript, PHP, Rust, TypeScript, Go, Java, and Python.

## Installation

### Quick install (PyPI)

```bash
pip install treesitter-mcp

# or with uvx (no global install)
uvx treesitter-mcp --help

# or install the binary with uv tool
uv tool install treesitter-mcp
```

This provides two commands:
-   `treesitter`: CLI for analyzing files
-   `treesitter-mcp`: MCP server

Check available options:
```bash
treesitter --help
treesitter-mcp --help
```

## Usage

### CLI

The CLI is available as the `treesitter` command after installation.

```bash
treesitter <file_path> [options]
```

#### Examples

**Get AST:**
```bash
treesitter test.c --ast
```

**Find Function Definition:**
```bash
treesitter test.c --find-function my_func
```

**Find Usages:**
```bash
treesitter test.c --find-usage my_func
```

**Get Dependencies:**
```bash
treesitter test.c --dependencies
```

**Run Custom Query:**
```bash
treesitter test.c --query "(function_definition) @func"
```

### MCP Server

To run the MCP server:

```bash
treesitter-mcp
```

Configure your MCP client (e.g., Claude Desktop) to use this server. See `docs/MCP_USAGE.md` for detailed configuration instructions.

## Supported Languages

-   **C**: Full support (Symbols, Call Graph, Queries, Usage).
-   **C++**: Full support.
-   **JavaScript**: Full support.
-   **PHP**: Full support.
-   **Rust**: Full support.
-   **TypeScript**: Full support.
-   **Go**: Full support.
-   **Java**: Full support.
-   **Python**: Full support.

## Documentation

See the `docs/` directory for more details:
-   [API Reference](docs/API.md)
-   [MCP Server Usage](docs/MCP_USAGE.md)
-   [Architecture](docs/ARCHITECTURE.md)
