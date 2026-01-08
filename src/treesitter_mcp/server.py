from mcp.server.fastmcp import FastMCP
from .core.language_manager import LanguageManager
from .languages.python import PythonAnalyzer
from .languages.c import CAnalyzer
from .languages.cpp import CppAnalyzer
from .languages.javascript import JavaScriptAnalyzer
from .languages.php import PhpAnalyzer
from .languages.rust import RustAnalyzer
from .languages.typescript import TypeScriptAnalyzer
from .languages.go import GoAnalyzer
from .languages.java import JavaAnalyzer
from .languages.ruby import RubyAnalyzer

import os
import sys
from typing import Any, Optional

mcp = FastMCP("tree-sitter-analysis")
language_manager = LanguageManager()

selected_tools: Optional[set[str]] = None

analyzers = {
    "python": PythonAnalyzer(language_manager),
    "c": CAnalyzer(language_manager),
    "cpp": CppAnalyzer(language_manager),
    "javascript": JavaScriptAnalyzer(language_manager),
    "php": PhpAnalyzer(language_manager),
    "rust": RustAnalyzer(language_manager),
    "typescript": TypeScriptAnalyzer(language_manager),
    "go": GoAnalyzer(language_manager),
    "java": JavaAnalyzer(language_manager),
    "ruby": RubyAnalyzer(language_manager),
}


def get_analyzer(file_path: str):
    """Determine the appropriate analyzer for a given file path based on extension.

    Args:
        file_path: path to the file

    Returns:
        Analyzer instance or None if not supported
    """
    ext = os.path.splitext(file_path)[1]
    if ext == ".py":
        return analyzers["python"]
    elif ext == ".c":
        return analyzers["c"]
    elif ext in (".cpp", ".cc", ".cxx", ".h", ".hpp"):
        return analyzers["cpp"]
    elif ext in (".js", ".jsx", ".mjs", ".cjs"):
        return analyzers["javascript"]
    elif ext in (".php", ".phtml"):
        return analyzers["php"]
    elif ext == ".rs":
        return analyzers["rust"]
    elif ext in (".ts", ".tsx", ".cts", ".mts"):
        return analyzers["typescript"]
    elif ext == ".go":
        return analyzers["go"]
    elif ext == ".java":
        return analyzers["java"]
    elif ext == ".rb":
        return analyzers["ruby"]
    return None


def normalize_path(file_path: str) -> str:
    """Normalize file path by expanding user and resolving absolute path."""
    if not file_path:
        return ""
    return os.path.abspath(os.path.expanduser(file_path.strip()))


def should_register_tool(tool_name: str) -> bool:
    """Check if a tool should be registered based on --tools selection."""
    if selected_tools is None:
        return True
    return tool_name in selected_tools


def mcp_tool_if_enabled(tool_name: str):
    """Decorator factory that conditionally applies mcp.tool() based on --tools selection."""
    if should_register_tool(tool_name):
        return mcp.tool()
    else:

        def noop_decorator(func):
            return func

        return noop_decorator


@mcp_tool_if_enabled("treesitter_analyze_file")
def treesitter_analyze_file(file_path: str) -> Any:
    """Analyze a source code file and extract symbols (functions, classes, etc.).

    Args:
        file_path: Path to the source code file to analyze (supports .py, .c, .cpp, .h, .hpp)

    Returns:
        Dictionary containing:
        - file_path: The analyzed file path
        - language: Detected programming language
        - symbols: List of extracted symbols (functions, classes, etc.)
        - errors: Any parsing errors encountered

    Note: This function does not return the full AST to avoid serialization issues.
    Use treesitter_get_ast() if you need the complete AST.
    """

    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        result = analyzer.analyze(file_path, code)
        result_dict = result.model_dump()

        # Remove the AST to avoid protobuf serialization issues with large files
        result_dict.pop("ast", None)

        return result_dict
    except Exception as e:
        return {"error": f"Error analyzing file: {str(e)}"}


@mcp_tool_if_enabled("treesitter_get_call_graph")
def treesitter_get_call_graph(file_path: str) -> Any:
    """Generate a call graph showing function calls and their relationships.

    Args:
        file_path: Path to the source code file

    Returns:
        Dictionary containing:
        - nodes: List of CallGraphNode objects, each with:
          - name: Function name
          - location: Source location (start/end points)
          - calls: List of function names called by this function
    """

    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        tree = analyzer.parse(code)
        if hasattr(analyzer, "get_call_graph"):
            result = analyzer.get_call_graph(tree.root_node, file_path)
            result_dict = result.model_dump()

            return result_dict
        else:
            return {"error": "Call graph not supported for this language"}
    except Exception as e:
        return {"error": f"Error generating call graph: {str(e)}"}


@mcp_tool_if_enabled("treesitter_find_function")
def treesitter_find_function(file_path: str, name: str) -> Any:
    """Search for a specific function definition by name.

    Args:
        file_path: Path to the source code file
        name: Name of the function to find

    Returns:
        Dictionary containing:
        - query: The search query (function name)
        - matches: List of Symbol objects representing matching function definitions
    """

    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        tree = analyzer.parse(code)
        if hasattr(analyzer, "find_function"):
            result = analyzer.find_function(tree.root_node, file_path, name)
            result_dict = result.model_dump()

            return result_dict
        else:
            return {"error": "Function search not supported for this language"}
    except Exception as e:
        return {"error": f"Error finding function: {str(e)}"}


@mcp_tool_if_enabled("treesitter_find_variable")
def treesitter_find_variable(file_path: str, name: str) -> Any:
    """Search for variable declarations and usages by name.

    Args:
        file_path: Path to the source code file
        name: Name of the variable to find

    Returns:
        Dictionary containing:
        - query: The search query (variable name)
        - matches: List of Symbol objects representing variable declarations and usages
    """

    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        tree = analyzer.parse(code)
        if hasattr(analyzer, "find_variable"):
            result = analyzer.find_variable(tree.root_node, file_path, name)
            result_dict = result.model_dump()

            return result_dict
        else:
            return {"error": "Variable search not supported for this language"}
    except Exception as e:
        return {"error": f"Error finding variable: {str(e)}"}


@mcp_tool_if_enabled("treesitter_get_supported_languages")
def treesitter_get_supported_languages() -> list[str]:
    """Get a list of programming languages supported by the analyzer.

    Returns:
        List of supported language names (e.g., ['python', 'c', 'cpp'])
    """

    try:
        result = list(analyzers.keys())
        return result
    except Exception as e:
        return []


@mcp_tool_if_enabled("treesitter_get_ast")
def treesitter_get_ast(file_path: str, max_depth: int = -1) -> Any:
    """Extract the complete Abstract Syntax Tree (AST) from a source file.

    Args:
        file_path: Path to the source code file
        max_depth: Maximum depth of the AST to return. -1 for no limit (default).
                   Useful for large files to avoid serialization errors.

    Returns:
        Dictionary representing the AST root node with:
        - type: Node type (e.g., 'module', 'function_definition')
        - start_point: Starting position (row, column)
        - end_point: Ending position (row, column)
        - children: List of child AST nodes
        - text: Optional text content
        - id: Optional node identifier
    """

    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        tree = analyzer.parse(code)
        ast = analyzer._build_ast(tree.root_node, code, max_depth=max_depth)
        result_dict = ast.model_dump()

        return result_dict
    except Exception as e:
        return {"error": f"Error getting AST: {str(e)}"}


@mcp_tool_if_enabled("treesitter_get_node_at_point")
def treesitter_get_node_at_point(
    file_path: str, row: int, column: int, max_depth: int = 0
) -> Any:
    """Return the AST node covering a specific point (row, column)."""
    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        ast = analyzer.build_node_at_point(
            code, row=row, column=column, max_depth=max_depth
        )
        return ast.model_dump()
    except Exception as e:
        return {"error": f"Error getting node at point: {str(e)}"}


@mcp_tool_if_enabled("treesitter_get_node_for_range")
def treesitter_get_node_for_range(
    file_path: str,
    start_row: int,
    start_column: int,
    end_row: int,
    end_column: int,
    max_depth: int = 0,
) -> Any:
    """Return the smallest AST node covering a point range."""
    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        ast = analyzer.build_node_for_range(
            code,
            start_row=start_row,
            start_col=start_column,
            end_row=end_row,
            end_col=end_column,
            max_depth=max_depth,
        )
        return ast.model_dump()
    except Exception as e:
        return {"error": f"Error getting node for range: {str(e)}"}


@mcp_tool_if_enabled("treesitter_cursor_walk")
def treesitter_cursor_walk(
    file_path: str, row: int, column: int, max_depth: int = 1
) -> Any:
    """Return a cursor-style view (focus node + context) at a point."""
    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        result = analyzer.build_cursor_view(
            code, row=row, column=column, max_depth=max_depth
        )
        return result
    except Exception as e:
        return {"error": f"Error walking cursor: {str(e)}"}


@mcp_tool_if_enabled("treesitter_get_source_for_range")
def treesitter_get_source_for_range(
    file_path: str,
    start_row: int,
    start_column: int,
    end_row: int,
    end_column: int,
) -> Any:
    """Extract the source code text for a given line/column range.

    Args:
        file_path: Path to the source code file
        start_row: Starting line number (0-based)
        start_column: Starting column number (0-based)
        end_row: Ending line number (0-based)
        end_column: Ending column number (0-based)

    Returns:
        Dictionary containing:
        - file_path: The analyzed file path
        - range: The requested range
        - source: The extracted source code text
    """
    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        source = analyzer.get_source_for_range(
            code,
            start_row=start_row,
            start_col=start_column,
            end_row=end_row,
            end_col=end_column,
        )

        return {
            "file_path": file_path,
            "range": {
                "start": {"row": start_row, "column": start_column},
                "end": {"row": end_row, "column": end_column},
            },
            "source": source,
        }
    except Exception as e:
        return {"error": f"Error getting source for range: {str(e)}"}


@mcp_tool_if_enabled("treesitter_run_query")
def treesitter_run_query(query: str, file_path: str, language: str = None) -> Any:
    """Execute a custom Tree-sitter query against a source file.

    Args:
        query: Tree-sitter query string in S-expression format
        file_path: Path to the source code file
        language: Optional language override (auto-detected from file extension if not provided)

    Returns:
        Query results as a dictionary or list, depending on the query structure
    """

    # If language is provided, we could potentially force it, but usually file extension is enough.
    # The request mentioned language="c", so we should handle it if passed, or rely on file path.

    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        tree = analyzer.parse(code)
        results = analyzer.run_query(query, tree.root_node, code)

        return results
    except Exception as e:
        return {"error": f"Error running query: {str(e)}"}


@mcp_tool_if_enabled("treesitter_find_usage")
def treesitter_find_usage(name: str, file_path: str, language: str = None) -> Any:
    """Find all usages/references of a symbol (identifier) in a source file.

    Args:
        name: Symbol name to search for
        file_path: Path to the source code file
        language: Optional language override (auto-detected from file extension if not provided)

    Returns:
        Dictionary containing:
        - query: The search query (symbol name)
        - matches: List of Symbol objects representing all usages of the symbol
    """

    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        tree = analyzer.parse(code)
        result = analyzer.find_usage(tree.root_node, file_path, name)
        result_dict = result.model_dump()

        return result_dict
    except Exception as e:
        return {"error": f"Error finding usage: {str(e)}"}


@mcp_tool_if_enabled("treesitter_get_dependencies")
def treesitter_get_dependencies(file_path: str) -> Any:
    """Extract all dependencies (imports/includes) from a source file.

    Args:
        file_path: Path to the source code file

    Returns:
        List of dependency strings:
        - For Python: import module names
        - For C/C++: included file paths (without quotes/brackets)
    """

    try:
        file_path = normalize_path(file_path)
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        analyzer = get_analyzer(file_path)
        if not analyzer:
            return {"error": f"Unsupported file type: {file_path}"}

        with open(file_path, "r") as f:
            code = f.read()

        tree = analyzer.parse(code)
        dependencies = analyzer.get_dependencies(tree.root_node, file_path)

        return dependencies
    except Exception as e:
        return {"error": f"Error getting dependencies: {str(e)}"}


def main():
    """Main entry point for the MCP server."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Code Analysis MCP Server")
    parser.add_argument(
        "--http", action="store_true", help="Run in streamable HTTP mode"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the HTTP server on (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to run the HTTP server on (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--tools",
        type=str,
        help="Comma-separated list of tools to expose (e.g., treesitter_analyze_file,treesitter_get_ast). If not provided, all tools are exposed.",
    )
    args = parser.parse_args()

    global selected_tools
    if args.tools:
        selected_tools = set(tool.strip() for tool in args.tools.split(","))
        print(
            f"Exposing {len(selected_tools)} selected tools: {', '.join(sorted(selected_tools))}",
            file=sys.stderr,
        )
    else:
        print("Exposing all tools", file=sys.stderr)

    print("Starting Code Analysis MCP Server...", file=sys.stderr)

    if args.http:
        mcp.settings.port = args.port
        mcp.settings.host = args.host
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
