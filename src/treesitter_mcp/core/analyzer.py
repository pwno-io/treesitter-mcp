from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from tree_sitter import Node, Tree
from .models import AnalysisResult, ASTNode, Point, Symbol, CallGraph, SearchResult

class BaseAnalyzer(ABC):
    """Abstract base class for language-specific analyzers."""
    def __init__(self, language_manager):
        """Initialize the analyzer with a language manager.
        
        Args:
            language_manager: Instance of LanguageManager
        """
        self.language_manager = language_manager

    @abstractmethod
    def get_language_name(self) -> str:
        """Get the unique name of the language (e.g., 'python', 'c')."""
        pass

    def parse(self, code: str) -> Tree:
        """Parse source code into a Tree-sitter tree.
        
        Args:
            code: Source code as string
            
        Returns:
            Tree-sitter Tree object
        """
        parser = self.language_manager.get_parser(self.get_language_name())
        return parser.parse(bytes(code, "utf8"))

    def analyze(self, file_path: str, code: str) -> AnalysisResult:
        """Perform comprehensive analysis on the code.
        
        Args:
            file_path: Path to the file
            code: Source code content
            
        Returns:
            AnalysisResult containing AST, symbols, etc.
        """
        tree = self.parse(code)
        ast = self._build_ast(tree.root_node, code)
        symbols = self.extract_symbols(tree.root_node, file_path)
        
        return AnalysisResult(
            file_path=file_path,
            language=self.get_language_name(),
            ast=ast,
            symbols=symbols
        )

    def _build_ast(self, node: Node, code: str, depth: int = 0, max_depth: int = -1) -> ASTNode:
        """Recursively build a simplified AST from the Tree-sitter tree."""
        start = Point(row=node.start_point[0], column=node.start_point[1])
        end = Point(row=node.end_point[0], column=node.end_point[1])
        
        children = []
        if max_depth == -1 or depth < max_depth:
            children = [self._build_ast(child, code, depth + 1, max_depth) for child in node.children]
        
        text = None
        if not children:
             text = node.text.decode('utf-8') if node.text else None

        return ASTNode(
            type=node.type,
            start_point=start,
            end_point=end,
            children=children,
            text=text,
            id=node.id
        )

    @abstractmethod
    def extract_symbols(self, root_node: Node, file_path: str) -> List[Symbol]:
        """Extract top-level symbols (functions, classes) from the AST."""
        pass

    @abstractmethod
    def get_call_graph(self, root_node: Node, file_path: str) -> CallGraph:
        """Generate a call graph from the AST."""
        pass

    @abstractmethod
    def find_function(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        """Find a function definition by name."""
        pass

    @abstractmethod
    def find_variable(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        """Find variable declarations and usages by name."""
        pass

    @abstractmethod
    def find_usage(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        """Find general usages of a symbol by name."""
        pass

    @abstractmethod
    def get_dependencies(self, root_node: Node, file_path: str) -> List[str]:
        """Extract dependencies (imports/includes) from the code."""
        pass

    def run_query(self, query_str: str, root_node: Node, code: str) -> List[Dict[str, Any]]:
        """Run a custom Tree-sitter S-expression query."""
        from tree_sitter import Query, QueryCursor
        language = self.language_manager.get_language(self.get_language_name())
        try:
            query = Query(language, query_str)
            cursor = QueryCursor(query)
            captures = cursor.captures(root_node)
            
            results = []
            for capture_name, nodes in captures.items():
                for node in nodes:
                    start = Point(row=node.start_point[0], column=node.start_point[1])
                    end = Point(row=node.end_point[0], column=node.end_point[1])
                    
                    text_content = node.text.decode('utf-8') if node.text else ""
                    results.append({
                        "capture_name": capture_name,
                        "text": text_content,
                        "start": start.model_dump(),
                        "end": end.model_dump(),
                        "type": node.type
                    })
            return results
        except Exception as e:
            raise ValueError(f"Invalid query: {e}")
