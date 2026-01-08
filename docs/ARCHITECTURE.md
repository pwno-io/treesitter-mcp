# Architecture

## Overview

The Code Analysis MCP Server is built on top of [Tree-sitter](https://tree-sitter.github.io/), a parser generator tool and an incremental parsing library. It uses Python bindings to interact with Tree-sitter.

## Components

### 1. Language Manager (`src/treesitter_mcp/core/language_manager.py`)
Responsible for loading Tree-sitter languages and parsers.
-   Manages `Language` and `Parser` instances.
-   Handles version-specific initialization (specifically for `tree-sitter` 0.21.3).

### 2. Analyzers (`src/treesitter_mcp/core/analyzer.py` & `src/treesitter_mcp/languages/`)
The core logic resides in the `BaseAnalyzer` class and its language-specific subclasses.
-   **`BaseAnalyzer`**: Defines the interface and common methods (`parse`, `_build_ast`, `run_query`, `get_source_for_range`).
-   **`CAnalyzer` (`c.py`)**: Implements C-specific logic (call graphs, includes).
-   **`CppAnalyzer` (`cpp.py`)**: Implements C++-specific logic.
-   **`JavaScriptAnalyzer` (`javascript.py`)**: Implements JavaScript-specific logic.
-   **`PhpAnalyzer` (`php.py`)**: Implements PHP-specific logic.
-   **`RustAnalyzer` (`rust.py`)**: Implements Rust-specific logic.
-   **`TypeScriptAnalyzer` (`typescript.py`)**: Implements TypeScript-specific logic.
-   **`GoAnalyzer` (`go.py`)**: Implements Go-specific logic.
-   **`JavaAnalyzer` (`java.py`)**: Implements Java-specific logic.
-   **`PythonAnalyzer` (`python.py`)**: Implements Python-specific logic (imports).

### 3. Interfaces
-   **CLI (`src/treesitter_mcp/cli.py`)**: A command-line wrapper around the analyzers.
-   **MCP Server (`src/treesitter_mcp/server.py`)**: Exposes analyzer functionality as MCP tools.

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
