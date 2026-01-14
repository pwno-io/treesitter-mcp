"""Command-line interface for Tree-sitter analysis tools."""

from typing import List, Optional, Dict, Any
import argparse
import sys

import orjson

from ..server import (
    treesitter_analyze_file,
    treesitter_get_ast,
    treesitter_get_call_graph,
    treesitter_find_function,
    treesitter_find_variable,
    treesitter_get_supported_languages,
    treesitter_get_node_at_point,
    treesitter_get_node_for_range,
    treesitter_cursor_walk,
    treesitter_get_source_for_range,
    treesitter_run_query,
    treesitter_find_usage,
    treesitter_get_dependencies,
)


def _print_json(data: Any) -> None:
    """Serialize data as pretty JSON to stdout."""
    json_bytes = orjson.dumps(data, option=orjson.OPT_INDENT_2)
    sys.stdout.buffer.write(json_bytes + b"\n")


def _build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for ts-cli.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Tree-sitter CLI for code analysis",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to the source file to analyze",
    )

    actions = parser.add_mutually_exclusive_group()
    actions.add_argument(
        "--ast",
        action="store_true",
        help="Output the full AST",
    )
    actions.add_argument(
        "--call-graph",
        action="store_true",
        help="Generate a call graph",
    )
    actions.add_argument(
        "--find-function",
        metavar="NAME",
        help="Find a function definition by name",
    )
    actions.add_argument(
        "--find-variable",
        metavar="NAME",
        help="Find variable declarations/usages by name",
    )
    actions.add_argument(
        "--find-usage",
        metavar="NAME",
        help="Find all usages of a symbol",
    )
    actions.add_argument(
        "--dependencies",
        action="store_true",
        help="List dependencies (imports/includes)",
    )
    actions.add_argument(
        "--query",
        metavar="QUERY",
        help="Run a custom Tree-sitter query",
    )
    actions.add_argument(
        "--source-range",
        nargs=4,
        type=int,
        metavar=("START_ROW", "START_COL", "END_ROW", "END_COL"),
        help="Extract source for a line/column range",
    )
    actions.add_argument(
        "--node-at-point",
        nargs=2,
        type=int,
        metavar=("ROW", "COLUMN"),
        help="Return AST node at a point",
    )
    actions.add_argument(
        "--node-for-range",
        nargs=4,
        type=int,
        metavar=("START_ROW", "START_COL", "END_ROW", "END_COL"),
        help="Return AST node for a range",
    )
    actions.add_argument(
        "--cursor-walk",
        nargs=2,
        type=int,
        metavar=("ROW", "COLUMN"),
        help="Return cursor-style node context at a point",
    )
    actions.add_argument(
        "--supported-languages",
        action="store_true",
        help="List supported languages",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        help="Max depth for AST/node/cursor outputs",
    )
    parser.add_argument(
        "--include-source",
        action="store_true",
        help="Include source for find-function/find-variable",
    )
    parser.add_argument(
        "--language",
        type=str,
        help="Override language for query/find-usage",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Write results to a file instead of stdout",
    )

    return parser


def _resolve_action(args: argparse.Namespace) -> Optional[str]:
    """Determine which action was requested.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Action identifier string or None for default analysis.
    """
    if args.ast:
        return "ast"
    if args.call_graph:
        return "call_graph"
    if args.find_function:
        return "find_function"
    if args.find_variable:
        return "find_variable"
    if args.find_usage:
        return "find_usage"
    if args.dependencies:
        return "dependencies"
    if args.query:
        return "query"
    if args.source_range:
        return "source_range"
    if args.node_at_point:
        return "node_at_point"
    if args.node_for_range:
        return "node_for_range"
    if args.cursor_walk:
        return "cursor_walk"
    if args.supported_languages:
        return "supported_languages"
    return None


def _validate_args(
    args: argparse.Namespace, parser: argparse.ArgumentParser, action: Optional[str]
) -> None:
    """Validate argument combinations before execution.

    Args:
        args: Parsed CLI arguments.
        parser: Argument parser for error reporting.
        action: Resolved action name.
    """
    if action != "supported_languages" and not args.file:
        parser.error("file path is required unless --supported-languages is set")

    if args.include_source and action not in {"find_function", "find_variable"}:
        parser.error(
            "--include-source only works with --find-function or --find-variable"
        )

    if args.language and action not in {"find_usage", "query"}:
        parser.error("--language only works with --find-usage or --query")

    if args.max_depth is not None and action not in {
        "ast",
        "node_at_point",
        "node_for_range",
        "cursor_walk",
    }:
        parser.error(
            "--max-depth only works with --ast, --node-at-point, --node-for-range, or --cursor-walk"
        )


def _handle_result(result: Any) -> int:
    """Print results and return exit code.

    Args:
        result: Tool result payload.

    Returns:
        Process exit code (0 for success, 1 for tool error).
    """
    if isinstance(result, dict) and "error" in result:
        _print_json(result)
        return 1
    _print_json(result)
    return 0


def _dispatch_action(action: Optional[str], args: argparse.Namespace) -> Any:
    """Dispatch the selected CLI action to the tool implementation.

    Args:
        action: Selected action identifier.
        args: Parsed CLI arguments.

    Returns:
        Tool result payload.
    """
    if action is None:
        return treesitter_analyze_file(
            file_path=args.file, output_file=args.output_file
        )

    if action == "ast":
        kwargs: Dict[str, Any] = {"file_path": args.file}
        if args.max_depth is not None:
            kwargs["max_depth"] = args.max_depth
        if args.output_file:
            kwargs["output_file"] = args.output_file
        return treesitter_get_ast(**kwargs)

    if action == "call_graph":
        return treesitter_get_call_graph(
            file_path=args.file, output_file=args.output_file
        )

    if action == "find_function":
        kwargs = {
            "file_path": args.file,
            "name": args.find_function,
            "include_source": args.include_source,
        }
        if args.output_file:
            kwargs["output_file"] = args.output_file
        return treesitter_find_function(**kwargs)

    if action == "find_variable":
        kwargs = {
            "file_path": args.file,
            "name": args.find_variable,
            "include_source": args.include_source,
        }
        if args.output_file:
            kwargs["output_file"] = args.output_file
        return treesitter_find_variable(**kwargs)

    if action == "find_usage":
        kwargs = {"name": args.find_usage, "file_path": args.file}
        if args.language:
            kwargs["language"] = args.language
        if args.output_file:
            kwargs["output_file"] = args.output_file
        return treesitter_find_usage(**kwargs)

    if action == "dependencies":
        return treesitter_get_dependencies(
            file_path=args.file, output_file=args.output_file
        )

    if action == "query":
        kwargs = {"query": args.query, "file_path": args.file}
        if args.language:
            kwargs["language"] = args.language
        if args.output_file:
            kwargs["output_file"] = args.output_file
        return treesitter_run_query(**kwargs)

    if action == "source_range":
        start_row, start_col, end_row, end_col = args.source_range
        kwargs = {
            "file_path": args.file,
            "start_row": start_row,
            "start_column": start_col,
            "end_row": end_row,
            "end_column": end_col,
        }
        if args.output_file:
            kwargs["output_file"] = args.output_file
        return treesitter_get_source_for_range(**kwargs)

    if action == "node_at_point":
        row, column = args.node_at_point
        kwargs = {"file_path": args.file, "row": row, "column": column}
        if args.max_depth is not None:
            kwargs["max_depth"] = args.max_depth
        if args.output_file:
            kwargs["output_file"] = args.output_file
        return treesitter_get_node_at_point(**kwargs)

    if action == "node_for_range":
        start_row, start_col, end_row, end_col = args.node_for_range
        kwargs = {
            "file_path": args.file,
            "start_row": start_row,
            "start_column": start_col,
            "end_row": end_row,
            "end_column": end_col,
        }
        if args.max_depth is not None:
            kwargs["max_depth"] = args.max_depth
        if args.output_file:
            kwargs["output_file"] = args.output_file
        return treesitter_get_node_for_range(**kwargs)

    if action == "cursor_walk":
        row, column = args.cursor_walk
        kwargs = {"file_path": args.file, "row": row, "column": column}
        if args.max_depth is not None:
            kwargs["max_depth"] = args.max_depth
        if args.output_file:
            kwargs["output_file"] = args.output_file
        return treesitter_cursor_walk(**kwargs)

    if action == "supported_languages":
        return treesitter_get_supported_languages(output_file=args.output_file)

    return {"error": f"Unsupported action: {action}"}


def main(argv: Optional[List[str]] = None) -> int:
    """Run the ts-cli command.

    Args:
        argv: Optional list of CLI arguments (defaults to sys.argv).

    Returns:
        Process exit code.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    action = _resolve_action(args)
    _validate_args(args, parser, action)

    try:
        result = _dispatch_action(action, args)
    except Exception as exc:
        _print_json({"error": f"Unexpected error: {exc}"})
        return 1

    return _handle_result(result)


if __name__ == "__main__":
    sys.exit(main())
