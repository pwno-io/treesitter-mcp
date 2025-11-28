import argparse
import sys
import os
from .core.language_manager import LanguageManager
from .languages.python import PythonAnalyzer
from .languages.c import CAnalyzer
from .languages.cpp import CppAnalyzer

def main():
    parser = argparse.ArgumentParser(description="Tree-sitter Analysis CLI")
    parser.add_argument("file", help="File to analyze")
    parser.add_argument("--call-graph", action="store_true", help="Generate call graph")
    parser.add_argument("--find-function", help="Find function by name")
    parser.add_argument("--find-variable", help="Find variable by name")
    parser.add_argument("--ast", action="store_true", help="Get AST")
    parser.add_argument("--query", help="Run a tree-sitter query")
    parser.add_argument("--find-usage", help="Find usages of a symbol")
    parser.add_argument("--dependencies", action="store_true", help="Get dependencies")
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
            ast = analyzer._build_ast(tree.root_node, code)
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
