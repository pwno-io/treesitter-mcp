# Code Analysis MCP Server

A Model Context Protocol (MCP) server for code analysis using Tree-sitter. This tool provides capabilities to parse code, extract symbols, generate call graphs, find usages, and run custom queries against C, C++, and Python code.

## Features

-   **AST Retrieval**: Get the full Abstract Syntax Tree (AST) of a file.
-   **Symbol Extraction**: Find function and variable definitions.
-   **Call Graph**: Generate a call graph for C/C++ functions.
-   **Tree-sitter Queries**: Run custom S-expression queries against your code.
-   **Usage Finder**: Find usages of functions and variables.
-   **Dependency Extraction**: List file dependencies (includes/imports).
-   **Multi-Language Support**: Currently supports C, C++, and Python.

## Installation

### Prerequisites

-   Python 3.10+
-   `pip`

### Setup

1.  Clone the repository.
2.  Install the package in editable mode:
    ```bash
    # Using uv (recommended)
    uv pip install -e .
    
    # Or using pip
    pip install -e .
    ```

This will install two command-line tools:
-   `code-analysis`: The CLI for analyzing files
-   `code-analysis-server`: The MCP server

You can now use these commands from anywhere on your system.

## Usage

### CLI

The CLI is available as the `code-analysis` command after installation.

```bash
code-analysis <file_path> [options]
```

#### Examples

**Get AST:**
```bash
code-analysis test.c --ast
```

**Find Function Definition:**
```bash
code-analysis test.c --find-function my_func
```

**Find Usages:**
```bash
code-analysis test.c --find-usage my_func
```

**Get Dependencies:**
```bash
code-analysis test.c --dependencies
```

**Run Custom Query:**
```bash
code-analysis test.c --query "(function_definition) @func"
```

### MCP Server

To run the MCP server:

```bash
code-analysis-server
```

Configure your MCP client (e.g., Claude Desktop) to use this server. See `docs/MCP_USAGE.md` for detailed configuration instructions.

## Supported Languages

-   **C**: Full support (Symbols, Call Graph, Queries, Usage).
-   **C++**: Full support.
-   **Python**: Full support.

## Documentation

See the `docs/` directory for more details:
-   [API Reference](docs/API.md)
-   [MCP Server Usage](docs/MCP_USAGE.md)
-   [Architecture](docs/ARCHITECTURE.md)
