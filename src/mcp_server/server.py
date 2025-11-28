from mcp.server.fastmcp import FastMCP
from .core.language_manager import LanguageManager
from .languages.python import PythonAnalyzer
from .languages.c import CAnalyzer
from .languages.cpp import CppAnalyzer
from .languages.cpp import CppAnalyzer
import os
import sys
from typing import Any

mcp = FastMCP("tree-sitter-analysis")
language_manager = LanguageManager()

analyzers = {
    'python': PythonAnalyzer(language_manager),
    'c': CAnalyzer(language_manager),
    'cpp': CppAnalyzer(language_manager),
}

def get_analyzer(file_path: str):
    ext = os.path.splitext(file_path)[1]
    if ext == '.py':
        return analyzers['python']
    elif ext == '.c':
        return analyzers['c']
    elif ext in ('.cpp', '.cc', '.cxx', '.h', '.hpp'):
        return analyzers['cpp']
    return None

@mcp.tool()
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
    print(f"[TOOL CALL] treesitter_analyze_file(file_path={file_path})", file=sys.stderr)
    analyzer = get_analyzer(file_path)
    if not analyzer:
        result = {"error": f"Unsupported file type: {file_path}"}
        print(f"[TOOL RETURN] treesitter_analyze_file -> {type(result)}: {result}", file=sys.stderr)
        return result
    
    try:
        with open(file_path, 'r') as f:
            code = f.read()
            
        result = analyzer.analyze(file_path, code)
        result_dict = result.model_dump()
        
        # Remove the AST to avoid protobuf serialization issues with large files
        result_dict.pop('ast', None)
        
        print(f"[TOOL RETURN] treesitter_analyze_file -> {type(result_dict)}: keys={list(result_dict.keys())}", file=sys.stderr)
        return result_dict
    except Exception as e:
        result = {"error": f"Error analyzing file: {str(e)}"}
        print(f"[TOOL RETURN] treesitter_analyze_file -> {type(result)}: {result}", file=sys.stderr)
        return result

@mcp.tool()
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
    print(f"[TOOL CALL] treesitter_get_call_graph(file_path={file_path})", file=sys.stderr)
    analyzer = get_analyzer(file_path)
    if not analyzer:
        result = {"error": f"Unsupported file type: {file_path}"}
        print(f"[TOOL RETURN] treesitter_get_call_graph -> {type(result)}: {result}", file=sys.stderr)
        return result
        
    try:
        with open(file_path, 'r') as f:
            code = f.read()
            
        tree = analyzer.parse(code)
        if hasattr(analyzer, 'get_call_graph'):
            result = analyzer.get_call_graph(tree.root_node, file_path)
            result_dict = result.model_dump()
            print(f"[TOOL RETURN] treesitter_get_call_graph -> {type(result_dict)}: keys={list(result_dict.keys())}", file=sys.stderr)
            return result_dict
        else:
            result = {"error": "Call graph not supported for this language"}
            print(f"[TOOL RETURN] treesitter_get_call_graph -> {type(result)}: {result}", file=sys.stderr)
            return result
    except Exception as e:
        result = {"error": f"Error generating call graph: {str(e)}"}
        print(f"[TOOL RETURN] treesitter_get_call_graph -> {type(result)}: {result}", file=sys.stderr)
        return result

@mcp.tool()
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
    print(f"[TOOL CALL] treesitter_find_function(file_path={file_path}, name={name})", file=sys.stderr)
    analyzer = get_analyzer(file_path)
    if not analyzer:
        result = {"error": f"Unsupported file type: {file_path}"}
        print(f"[TOOL RETURN] treesitter_find_function -> {type(result)}: {result}", file=sys.stderr)
        return result
        
    try:
        with open(file_path, 'r') as f:
            code = f.read()
            
        tree = analyzer.parse(code)
        if hasattr(analyzer, 'find_function'):
            result = analyzer.find_function(tree.root_node, file_path, name)
            result_dict = result.model_dump()
            print(f"[TOOL RETURN] treesitter_find_function -> {type(result_dict)}: keys={list(result_dict.keys())}", file=sys.stderr)
            return result_dict
        else:
            result = {"error": "Function search not supported for this language"}
            print(f"[TOOL RETURN] treesitter_find_function -> {type(result)}: {result}", file=sys.stderr)
            return result
    except Exception as e:
        result = {"error": f"Error finding function: {str(e)}"}
        print(f"[TOOL RETURN] treesitter_find_function -> {type(result)}: {result}", file=sys.stderr)
        return result

@mcp.tool()
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
    print(f"[TOOL CALL] treesitter_find_variable(file_path={file_path}, name={name})", file=sys.stderr)
    analyzer = get_analyzer(file_path)
    if not analyzer:
        result = {"error": f"Unsupported file type: {file_path}"}
        print(f"[TOOL RETURN] treesitter_find_variable -> {type(result)}: {result}", file=sys.stderr)
        return result
        
    try:
        with open(file_path, 'r') as f:
            code = f.read()
            
        tree = analyzer.parse(code)
        if hasattr(analyzer, 'find_variable'):
            result = analyzer.find_variable(tree.root_node, file_path, name)
            result_dict = result.model_dump()
            print(f"[TOOL RETURN] treesitter_find_variable -> {type(result_dict)}: keys={list(result_dict.keys())}", file=sys.stderr)
            return result_dict
        else:
            result = {"error": "Variable search not supported for this language"}
            print(f"[TOOL RETURN] treesitter_find_variable -> {type(result)}: {result}", file=sys.stderr)
            return result
    except Exception as e:
        result = {"error": f"Error finding variable: {str(e)}"}
        print(f"[TOOL RETURN] treesitter_find_variable -> {type(result)}: {result}", file=sys.stderr)
        return result

@mcp.tool()
def treesitter_get_supported_languages() -> list[str]:
    """Get a list of programming languages supported by the analyzer.
    
    Returns:
        List of supported language names (e.g., ['python', 'c', 'cpp'])
    """
    print(f"[TOOL CALL] treesitter_get_supported_languages()", file=sys.stderr)
    result = list(analyzers.keys())
    print(f"[TOOL RETURN] treesitter_get_supported_languages -> {type(result)}: {result}", file=sys.stderr)
    return result

@mcp.tool()
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
    print(f"[TOOL CALL] treesitter_get_ast(file_path={file_path}, max_depth={max_depth})", file=sys.stderr)
    analyzer = get_analyzer(file_path)
    if not analyzer:
        result = {"error": f"Unsupported file type: {file_path}"}
        print(f"[TOOL RETURN] treesitter_get_ast -> {type(result)}: {result}", file=sys.stderr)
        return result
        
    try:
        with open(file_path, 'r') as f:
            code = f.read()
            
        tree = analyzer.parse(code)
        ast = analyzer._build_ast(tree.root_node, code, max_depth=max_depth)
        result_dict = ast.model_dump()
        print(f"[TOOL RETURN] treesitter_get_ast -> {type(result_dict)}: keys={list(result_dict.keys())}", file=sys.stderr)
        return result_dict
    except Exception as e:
        result = {"error": f"Error getting AST: {str(e)}"}
        print(f"[TOOL RETURN] treesitter_get_ast -> {type(result)}: {result}", file=sys.stderr)
        return result

@mcp.tool()
def treesitter_run_query(query: str, file_path: str, language: str = None) -> Any:
    """Execute a custom Tree-sitter query against a source file.
    
    Args:
        query: Tree-sitter query string in S-expression format
        file_path: Path to the source code file
        language: Optional language override (auto-detected from file extension if not provided)
    
    Returns:
        Query results as a dictionary or list, depending on the query structure
    """
    print(f"[TOOL CALL] treesitter_run_query(query={query[:50]}..., file_path={file_path}, language={language})", file=sys.stderr)
    # If language is provided, we could potentially force it, but usually file extension is enough.
    # The request mentioned language="c", so we should handle it if passed, or rely on file path.
    
    analyzer = get_analyzer(file_path)
    if not analyzer:
        result = {"error": f"Unsupported file type: {file_path}"}
        print(f"[TOOL RETURN] treesitter_run_query -> {type(result)}: {result}", file=sys.stderr)
        return result
        
    try:
        with open(file_path, 'r') as f:
            code = f.read()
            
        tree = analyzer.parse(code)
        results = analyzer.run_query(query, tree.root_node, code)
        print(f"[TOOL RETURN] treesitter_run_query -> {type(results)}", file=sys.stderr)
        return results
    except Exception as e:
        result = {"error": f"Error running query: {str(e)}"}
        print(f"[TOOL RETURN] treesitter_run_query -> {type(result)}: {result}", file=sys.stderr)
        return result

@mcp.tool()
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
    print(f"[TOOL CALL] treesitter_find_usage(name={name}, file_path={file_path}, language={language})", file=sys.stderr)
    analyzer = get_analyzer(file_path)
    if not analyzer:
        result = {"error": f"Unsupported file type: {file_path}"}
        print(f"[TOOL RETURN] treesitter_find_usage -> {type(result)}: {result}", file=sys.stderr)
        return result
        
    try:
        with open(file_path, 'r') as f:
            code = f.read()
            
        tree = analyzer.parse(code)
        result = analyzer.find_usage(tree.root_node, file_path, name)
        result_dict = result.model_dump()
        print(f"[TOOL RETURN] treesitter_find_usage -> {type(result_dict)}: keys={list(result_dict.keys())}", file=sys.stderr)
        return result_dict
    except Exception as e:
        result = {"error": f"Error finding usage: {str(e)}"}
        print(f"[TOOL RETURN] treesitter_find_usage -> {type(result)}: {result}", file=sys.stderr)
        return result

@mcp.tool()
def treesitter_get_dependencies(file_path: str) -> Any:
    """Extract all dependencies (imports/includes) from a source file.
    
    Args:
        file_path: Path to the source code file
    
    Returns:
        List of dependency strings:
        - For Python: import module names
        - For C/C++: included file paths (without quotes/brackets)
    """
    print(f"[TOOL CALL] treesitter_get_dependencies(file_path={file_path})", file=sys.stderr)
    analyzer = get_analyzer(file_path)
    if not analyzer:
        result = {"error": f"Unsupported file type: {file_path}"}
        print(f"[TOOL RETURN] treesitter_get_dependencies -> {type(result)}: {result}", file=sys.stderr)
        return result
        
    try:
        with open(file_path, 'r') as f:
            code = f.read()
            
        tree = analyzer.parse(code)
        dependencies = analyzer.get_dependencies(tree.root_node, file_path)
        print(f"[TOOL RETURN] treesitter_get_dependencies -> {type(dependencies)}: {dependencies}", file=sys.stderr)
        return dependencies
    except Exception as e:
        result = {"error": f"Error getting dependencies: {str(e)}"}
        print(f"[TOOL RETURN] treesitter_get_dependencies -> {type(result)}: {result}", file=sys.stderr)
        return result

def main():
    import sys
    print("Starting Code Analysis MCP Server...", file=sys.stderr)
    mcp.run()

if __name__ == "__main__":
    main()

