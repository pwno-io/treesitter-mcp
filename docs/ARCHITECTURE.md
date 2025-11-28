# Architecture

## Overview

The Code Analysis MCP Server is built on top of [Tree-sitter](https://tree-sitter.github.io/), a parser generator tool and an incremental parsing library. It uses Python bindings to interact with Tree-sitter.

## Components

### 1. Language Manager (`src/mcp_server/core/language_manager.py`)
Responsible for loading Tree-sitter languages and parsers.
-   Manages `Language` and `Parser` instances.
-   Handles version-specific initialization (specifically for `tree-sitter` 0.21.3).

### 2. Analyzers (`src/mcp_server/core/analyzer.py` & `src/mcp_server/languages/`)
The core logic resides in the `BaseAnalyzer` class and its language-specific subclasses.
-   **`BaseAnalyzer`**: Defines the interface and common methods (`parse`, `_build_ast`, `run_query`).
-   **`CAnalyzer` (`c.py`)**: Implements C-specific logic (call graphs, includes).
-   **`CppAnalyzer` (`cpp.py`)**: Implements C++-specific logic.
-   **`PythonAnalyzer` (`python.py`)**: Implements Python-specific logic (imports).

### 3. Interfaces
-   **CLI (`src/mcp_server/cli.py`)**: A command-line wrapper around the analyzers.
-   **MCP Server (`src/mcp_server/server.py`)**: Exposes analyzer functionality as MCP tools.

## Tree-sitter Versioning

This project is explicitly pinned to `tree-sitter==0.21.3`.
-   **API Changes**: Newer versions of Tree-sitter introduced breaking changes (e.g., `Query` object changes, `captures` return type).
-   **Compatibility**: The codebase handles `Query.captures()` returning a list of tuples `(Node, str)` and `Node.start_point` being a tuple `(row, col)`.

## Extensibility

To add a new language:
1.  Install the corresponding tree-sitter binding (e.g., `pip install tree-sitter-go==0.21.0`).
2.  Update `LanguageManager` to load the new language.
3.  Create a new analyzer class (e.g., `GoAnalyzer`) inheriting from `BaseAnalyzer`.
4.  Implement abstract methods (`extract_symbols`, `find_usage`, etc.).
5.  Register the analyzer in `cli.py` and `server.py`.
