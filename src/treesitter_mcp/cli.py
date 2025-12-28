import argparse
import sys
import os
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

def main():
    class _HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass

    parser = argparse.ArgumentParser(
        description="Tree-sitter CLI for AST, symbols, call graphs, and code queries (multi-language).",
        formatter_class=_HelpFormatter,
        epilog="""Examples:
  treesitter sample.c   --ast
  treesitter sample.cpp --call-graph
  treesitter sample.py  --find-function foo
  treesitter sample.js  --find-usage myVar
  treesitter sample.ts  --query "(function_declaration) @fn"
  treesitter sample.rs  --dependencies
""",
    )

    parser.add_argument("file", help="Source file to analyze")
    parser.add_argument("--call-graph", action="store_true", help="Generate call graph for functions")
    parser.add_argument("--find-function", help="Find function definition by exact name")
    parser.add_argument("--find-variable", help="Find variable definition by exact name")
    parser.add_argument("--ast", action="store_true", help="Print AST (optionally limited by --max-depth)")
    parser.add_argument("--node-at", nargs=2, type=int, metavar=("ROW", "COL"), help="Get AST node covering a point (0-based row, col)")
    parser.add_argument("--range", dest="range_points", nargs=4, type=int, metavar=("START_ROW", "START_COL", "END_ROW", "END_COL"), help="Get AST node covering a range (0-based positions)")
    parser.add_argument("--cursor", nargs=2, type=int, metavar=("ROW", "COL"), help="Cursor-style view (ancestors/siblings/children) at a point")
    parser.add_argument("--max-depth", type=int, default=-1, help="Limit AST depth for AST/node/range/cursor outputs (-1 for full tree)")
    parser.add_argument("--query", help="Run a raw tree-sitter S-expression query")
    parser.add_argument("--find-usage", help="Find usages of a symbol by exact name")
    parser.add_argument("--dependencies", action="store_true", help="List includes/imports/dependencies")
    args = parser.parse_args()
    
    file_path = os.path.abspath(args.file)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
        
    language_manager = LanguageManager()
    analyzers = {
        '.py': PythonAnalyzer(language_manager),
        '.c': CAnalyzer(language_manager),
        '.cpp': CppAnalyzer(language_manager),
        '.cc': CppAnalyzer(language_manager),
        '.cxx': CppAnalyzer(language_manager),
        '.h': CppAnalyzer(language_manager),
        '.hpp': CppAnalyzer(language_manager),
        '.js': JavaScriptAnalyzer(language_manager),
        '.jsx': JavaScriptAnalyzer(language_manager),
        '.mjs': JavaScriptAnalyzer(language_manager),
        '.cjs': JavaScriptAnalyzer(language_manager),
        '.php': PhpAnalyzer(language_manager),
        '.phtml': PhpAnalyzer(language_manager),
        '.rs': RustAnalyzer(language_manager),
        '.ts': TypeScriptAnalyzer(language_manager),
        '.tsx': TypeScriptAnalyzer(language_manager),
        '.cts': TypeScriptAnalyzer(language_manager),
        '.mts': TypeScriptAnalyzer(language_manager),
        '.go': GoAnalyzer(language_manager),
        '.java': JavaAnalyzer(language_manager),
    }
    
    ext = os.path.splitext(file_path)[1]
    analyzer = analyzers.get(ext)
    
    if not analyzer:
        if ext == '.h':
             analyzer = CAnalyzer(language_manager)
        else:
            print(f"Unsupported file extension: {ext}", file=sys.stderr)
            sys.exit(1)
            
    try:
        with open(file_path, 'r') as f:
            code = f.read()
            
        tree = analyzer.parse(code)
        
        if args.call_graph:
            if hasattr(analyzer, 'get_call_graph'):
                result = analyzer.get_call_graph(tree.root_node, file_path)
                print(result.model_dump_json(indent=2))
            else:
                print("Call graph not supported for this language", file=sys.stderr)
        elif args.node_at:
            row, col = args.node_at
            node = tree.root_node.descendant_for_point_range((row, col), (row, col))
            ast = analyzer._build_ast(node, code, max_depth=args.max_depth)
            print(ast.model_dump_json(indent=2))
        elif args.range_points:
            s_row, s_col, e_row, e_col = args.range_points
            node = tree.root_node.descendant_for_point_range((s_row, s_col), (e_row, e_col))
            ast = analyzer._build_ast(node, code, max_depth=args.max_depth)
            print(ast.model_dump_json(indent=2))
        elif args.cursor:
            row, col = args.cursor
            view = analyzer.build_cursor_view(code, row=row, column=col, max_depth=max(0, args.max_depth if args.max_depth != -1 else 1))
            import json
            print(json.dumps(view, indent=2))
        elif args.find_function:
            if hasattr(analyzer, 'find_function'):
                result = analyzer.find_function(tree.root_node, file_path, args.find_function)
                print(result.model_dump_json(indent=2))
            else:
                print("Function search not supported for this language", file=sys.stderr)
        elif args.find_variable:
            if hasattr(analyzer, 'find_variable'):
                result = analyzer.find_variable(tree.root_node, file_path, args.find_variable)
                print(result.model_dump_json(indent=2))
            else:
                print("Variable search not supported for this language", file=sys.stderr)
        elif args.ast:
            ast = analyzer._build_ast(tree.root_node, code, max_depth=args.max_depth)
            print(ast.model_dump_json(indent=2))
        elif args.query:
            results = analyzer.run_query(args.query, tree.root_node, code)
            import json
            print(json.dumps(results, indent=2))
        elif args.find_usage:
            result = analyzer.find_usage(tree.root_node, file_path, args.find_usage)
            print(result.model_dump_json(indent=2))
        elif args.dependencies:
            dependencies = analyzer.get_dependencies(tree.root_node, file_path)
            import json
            print(json.dumps(dependencies, indent=2))
        else:
            # Default analysis
            result = analyzer.analyze(file_path, code)
            print(result.model_dump_json(indent=2))
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error analyzing file: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
