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
import orjson

mcp = FastMCP("tree-sitter-analysis")
language_manager = LanguageManager()

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


def write_output_file(output_file: str, data: Any) -> dict:
    """Write result data to file efficiently using orjson.

    Args:
        output_file: Path to write the output to
        data: Data to serialize and write (dict, list, or Pydantic model)

    Returns:
        Success dict with file path and bytes written, or error dict
    """
    try:
        output_path = normalize_path(output_file)
        parent_dir = os.path.dirname(output_path)

        if os.path.exists(output_path):
            print(f"Warning: Overwriting existing file: {output_path}", file=sys.stderr)

        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        json_bytes = orjson.dumps(data, option=orjson.OPT_INDENT_2)

        with open(output_path, "wb") as f:
            bytes_written = f.write(json_bytes)

        return {
            "status": "written",
            "output_file": output_path,
            "bytes_written": bytes_written,
        }
    except Exception as e:
        return {"error": f"Failed to write output file: {str(e)}"}


# All tool functions defined below - registration happens in register_tools()


def treesitter_analyze_file(file_path: str, output_file: Optional[str] = None) -> Any:
    """Analyze a source code file and extract symbols (functions, classes, etc.).

    Args:
        file_path: Path to the source code file to analyze (supports .py, .c, .cpp, .h, .hpp)
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        Dictionary containing:
        - file_path: The analyzed file path
        - language: Detected programming language
        - symbols: List of extracted symbols (functions, classes, etc.)
        - errors: Any parsing errors encountered
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}

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

        result_dict.pop("ast", None)

        if output_file:
            return write_output_file(output_file, result_dict)
        return result_dict
    except Exception as e:
        return {"error": f"Error analyzing file: {str(e)}"}


def treesitter_get_call_graph(file_path: str, output_file: Optional[str] = None) -> Any:
    """Generate a call graph showing function calls and their relationships.

    Args:
        file_path: Path to the source code file
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        Dictionary containing:
        - nodes: List of CallGraphNode objects, each with:
          - name: Function name
          - location: Source location (start/end points)
          - calls: List of function names called by this function
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
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

            if output_file:
                return write_output_file(output_file, result_dict)
            return result_dict
        else:
            return {"error": "Call graph not supported for this language"}
    except Exception as e:
        return {"error": f"Error generating call graph: {str(e)}"}


def treesitter_find_function(
    file_path: str,
    name: str,
    include_source: bool = False,
    output_file: Optional[str] = None,
) -> Any:
    """Search for a specific function definition by name.

    Args:
        file_path: Path to the source code file
        name: Name of the function to find
        include_source: If True, includes the source code for each matched function.
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        Dictionary containing:
        - query: The search query (function name)
        - matches: List of Symbol objects representing matching function definitions.
                   If include_source is True, each match includes a "source" field.
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
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

            if include_source and result_dict.get("matches"):
                for match in result_dict["matches"]:
                    loc = match.get("location", {})
                    start = loc.get("start", {})
                    end = loc.get("end", {})
                    match["source"] = analyzer.get_source_for_range(
                        code,
                        start_row=start.get("row", 0),
                        start_col=start.get("column", 0),
                        end_row=end.get("row", 0),
                        end_col=end.get("column", 0),
                    )

            if output_file:
                return write_output_file(output_file, result_dict)
            return result_dict
        else:
            return {"error": "Function search not supported for this language"}
    except Exception as e:
        return {"error": f"Error finding function: {str(e)}"}


def treesitter_find_variable(
    file_path: str,
    name: str,
    include_source: bool = False,
    output_file: Optional[str] = None,
) -> Any:
    """Search for variable declarations and usages by name.

    Args:
        file_path: Path to the source code file
        name: Name of the variable to find
        include_source: If True, includes the source code for each matched variable.
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        Dictionary containing:
        - query: The search query (variable name)
        - matches: List of Symbol objects representing variable declarations and usages.
                   If include_source is True, each match includes a "source" field.
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
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

            if include_source and result_dict.get("matches"):
                for match in result_dict["matches"]:
                    loc = match.get("location", {})
                    start = loc.get("start", {})
                    end = loc.get("end", {})
                    match["source"] = analyzer.get_source_for_range(
                        code,
                        start_row=start.get("row", 0),
                        start_col=start.get("column", 0),
                        end_row=end.get("row", 0),
                        end_col=end.get("column", 0),
                    )

            if output_file:
                return write_output_file(output_file, result_dict)
            return result_dict
        else:
            return {"error": "Variable search not supported for this language"}
    except Exception as e:
        return {"error": f"Error finding variable: {str(e)}"}


def treesitter_get_supported_languages(output_file: Optional[str] = None) -> Any:
    """Get a list of programming languages supported by the analyzer.

    Args:
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        List of supported language names (e.g., ['python', 'c', 'cpp'])
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
    """

    try:
        result = list(analyzers.keys())
        if output_file:
            return write_output_file(output_file, result)
        return result
    except Exception as e:
        return []


def treesitter_get_ast(
    file_path: str, max_depth: int = -1, output_file: Optional[str] = None
) -> Any:
    """Extract the complete Abstract Syntax Tree (AST) from a source file.

    Args:
        file_path: Path to the source code file
        max_depth: Maximum depth of the AST to return. -1 for no limit (default).
                   Useful for large files to avoid serialization errors.
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        Dictionary representing the AST root node with:
        - type: Node type (e.g., 'module', 'function_definition')
        - start_point: Starting position (row, column)
        - end_point: Ending position (row, column)
        - children: List of child AST nodes
        - text: Optional text content
        - id: Optional node identifier
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
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

        if output_file:
            return write_output_file(output_file, result_dict)
        return result_dict
    except Exception as e:
        return {"error": f"Error getting AST: {str(e)}"}


def treesitter_get_node_at_point(
    file_path: str,
    row: int,
    column: int,
    max_depth: int = 0,
    output_file: Optional[str] = None,
) -> Any:
    """Return the AST node covering a specific point (row, column).

    Args:
        file_path: Path to the source code file
        row: Row number (0-based)
        column: Column number (0-based)
        max_depth: Maximum depth of the AST to return. 0 for just the node.
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        AST node as dictionary
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
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

        ast = analyzer.build_node_at_point(
            code, row=row, column=column, max_depth=max_depth
        )
        result_dict = ast.model_dump()
        if output_file:
            return write_output_file(output_file, result_dict)
        return result_dict
    except Exception as e:
        return {"error": f"Error getting node at point: {str(e)}"}


def treesitter_get_node_for_range(
    file_path: str,
    start_row: int,
    start_column: int,
    end_row: int,
    end_column: int,
    max_depth: int = 0,
    output_file: Optional[str] = None,
) -> Any:
    """Return the smallest AST node covering a point range.

    Args:
        file_path: Path to the source code file
        start_row: Starting row (0-based)
        start_column: Starting column (0-based)
        end_row: Ending row (0-based)
        end_column: Ending column (0-based)
        max_depth: Maximum depth of the AST to return. 0 for just the node.
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        AST node as dictionary
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
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

        ast = analyzer.build_node_for_range(
            code,
            start_row=start_row,
            start_col=start_column,
            end_row=end_row,
            end_col=end_column,
            max_depth=max_depth,
        )
        result_dict = ast.model_dump()
        if output_file:
            return write_output_file(output_file, result_dict)
        return result_dict
    except Exception as e:
        return {"error": f"Error getting node for range: {str(e)}"}


def treesitter_cursor_walk(
    file_path: str,
    row: int,
    column: int,
    max_depth: int = 1,
    output_file: Optional[str] = None,
) -> Any:
    """Return a cursor-style view (focus node + context) at a point.

    Args:
        file_path: Path to the source code file
        row: Row number (0-based)
        column: Column number (0-based)
        max_depth: Maximum depth of the AST to return.
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        Dictionary with focus, ancestors, siblings, and children
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
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

        result = analyzer.build_cursor_view(
            code, row=row, column=column, max_depth=max_depth
        )
        if output_file:
            return write_output_file(output_file, result)
        return result
    except Exception as e:
        return {"error": f"Error walking cursor: {str(e)}"}


def treesitter_get_source_for_range(
    file_path: str,
    start_row: int,
    start_column: int,
    end_row: int,
    end_column: int,
    output_file: Optional[str] = None,
) -> Any:
    """Extract the source code text for a given line/column range.

    Args:
        file_path: Path to the source code file
        start_row: Starting line number (0-based)
        start_column: Starting column number (0-based)
        end_row: Ending line number (0-based)
        end_column: Ending column number (0-based)
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        Dictionary containing:
        - file_path: The analyzed file path
        - range: The requested range
        - source: The extracted source code text
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
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

        result = {
            "file_path": file_path,
            "range": {
                "start": {"row": start_row, "column": start_column},
                "end": {"row": end_row, "column": end_column},
            },
            "source": source,
        }
        if output_file:
            return write_output_file(output_file, result)
        return result
    except Exception as e:
        return {"error": f"Error getting source for range: {str(e)}"}


def treesitter_run_query(
    query: str,
    file_path: str,
    language: Optional[str] = None,
    output_file: Optional[str] = None,
) -> Any:
    """Execute a custom Tree-sitter query against a source file.

    Args:
        query: Tree-sitter query string in S-expression format
        file_path: Path to the source code file
        language: Optional language override (auto-detected from file extension if not provided)
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        Query results as a dictionary or list, depending on the query structure
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
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
        results = analyzer.run_query(query, tree.root_node, code)

        if output_file:
            return write_output_file(output_file, results)
        return results
    except Exception as e:
        return {"error": f"Error running query: {str(e)}"}


def treesitter_find_usage(
    name: str,
    file_path: str,
    language: Optional[str] = None,
    output_file: Optional[str] = None,
) -> Any:
    """Find all usages/references of a symbol (identifier) in a source file.

    Args:
        name: Symbol name to search for
        file_path: Path to the source code file
        language: Optional language override (auto-detected from file extension if not provided)
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        Dictionary containing:
        - query: The search query (symbol name)
        - matches: List of Symbol objects representing all usages of the symbol
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
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

        if output_file:
            return write_output_file(output_file, result_dict)
        return result_dict
    except Exception as e:
        return {"error": f"Error finding usage: {str(e)}"}


def treesitter_get_dependencies(
    file_path: str, output_file: Optional[str] = None
) -> Any:
    """Extract all dependencies (imports/includes) from a source file.

    Args:
        file_path: Path to the source code file
        output_file: If provided, writes result to this file instead of returning.
                     Useful for large outputs to prevent context overload.

    Returns:
        List of dependency strings:
        - For Python: import module names
        - For C/C++: included file paths (without quotes/brackets)
        OR if output_file is set: {"status": "written", "output_file": "...", "bytes_written": N}
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

        if output_file:
            return write_output_file(output_file, dependencies)
        return dependencies
    except Exception as e:
        return {"error": f"Error getting dependencies: {str(e)}"}


# Map of all available tools - used for dynamic registration
ALL_TOOLS = {
    "treesitter_analyze_file": treesitter_analyze_file,
    "treesitter_get_call_graph": treesitter_get_call_graph,
    "treesitter_find_function": treesitter_find_function,
    "treesitter_find_variable": treesitter_find_variable,
    "treesitter_get_supported_languages": treesitter_get_supported_languages,
    "treesitter_get_ast": treesitter_get_ast,
    "treesitter_get_node_at_point": treesitter_get_node_at_point,
    "treesitter_get_node_for_range": treesitter_get_node_for_range,
    "treesitter_cursor_walk": treesitter_cursor_walk,
    "treesitter_get_source_for_range": treesitter_get_source_for_range,
    "treesitter_run_query": treesitter_run_query,
    "treesitter_find_usage": treesitter_find_usage,
    "treesitter_get_dependencies": treesitter_get_dependencies,
}


def register_tools(selected_tools: Optional[set[str]] = None) -> int:
    """Register tools with the MCP server.

    Args:
        selected_tools: Set of tool names to register. If None, all tools are registered.

    Returns:
        Number of tools registered.
    """
    count = 0
    for name, func in ALL_TOOLS.items():
        if selected_tools is None or name in selected_tools:
            mcp.tool()(func)
            count += 1
    return count


def main():
    """Main entry point for the MCP server."""
    import argparse

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
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all available tool names and exit.",
    )
    args = parser.parse_args()

    if args.list_tools:
        print("Available tools:")
        for name in sorted(ALL_TOOLS.keys()):
            print(f"  {name}")
        return

    selected_tools = None
    if args.tools:
        selected_tools = set(tool.strip() for tool in args.tools.split(","))
        # Validate tool names
        invalid = selected_tools - set(ALL_TOOLS.keys())
        if invalid:
            print(
                f"Error: Unknown tool(s): {', '.join(sorted(invalid))}", file=sys.stderr
            )
            print(f"Use --list-tools to see available tools.", file=sys.stderr)
            sys.exit(1)

    # Register tools after parsing arguments
    count = register_tools(selected_tools)
    print(f"Registered {count} tool(s)", file=sys.stderr)

    if selected_tools:
        print(f"Exposing: {', '.join(sorted(selected_tools))}", file=sys.stderr)
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
