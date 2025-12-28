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

    def _build_ast(self, node: Node, code: str, depth: int = 0, max_depth: int = -1, field_name: Optional[str] = None) -> ASTNode:
        """Recursively build a simplified AST from the Tree-sitter tree."""
        start = Point(row=node.start_point[0], column=node.start_point[1])
        end = Point(row=node.end_point[0], column=node.end_point[1])
        
        children: List[ASTNode] = []
        if max_depth == -1 or depth < max_depth:
            for idx, child in enumerate(node.children):
                child_field_name = node.field_name_for_child(idx)
                child_ast = self._build_ast(child, code, depth + 1, max_depth, field_name=child_field_name)
                children.append(child_ast)
        
        text = None
        if not children:
            text = node.text.decode('utf-8') if node.text else None

        return ASTNode(
            type=node.type,
            start_point=start,
            end_point=end,
            children=children,
            field_name=field_name,
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

    # Utility helpers for point/range navigation and cursor-style views
    def _field_name_for_child(self, parent: Node, child: Node) -> Optional[str]:
        """Return the field name of a child relative to its parent, if available."""
        for idx, candidate in enumerate(parent.children):
            if candidate.id == child.id:
                return parent.field_name_for_child(idx)
        return None

    def build_node_at_point(self, code: str, row: int, column: int, max_depth: int = 0) -> ASTNode:
        """Return the AST node covering a specific point (row, col)."""
        tree = self.parse(code)
        target = tree.root_node.descendant_for_point_range((row, column), (row, column))
        return self._build_ast(target, code, max_depth=max_depth)

    def build_node_for_range(self, code: str, start_row: int, start_col: int, end_row: int, end_col: int, max_depth: int = 0) -> ASTNode:
        """Return the smallest AST node covering a point range."""
        tree = self.parse(code)
        target = tree.root_node.descendant_for_point_range((start_row, start_col), (end_row, end_col))
        return self._build_ast(target, code, max_depth=max_depth)

    def build_cursor_view(self, code: str, row: int, column: int, max_depth: int = 1) -> Dict[str, Any]:
        """Return a compact cursor-style view around the node covering (row, col).

        Provides the focused node (limited depth), its ancestors, and nearby siblings.
        """
        tree = self.parse(code)
        target = tree.root_node.descendant_for_point_range((row, column), (row, column))

        def to_summary(node: Node, parent: Optional[Node]) -> Dict[str, Any]:
            field_name = self._field_name_for_child(parent, node) if parent else None
            return {
                "type": node.type,
                "field_name": field_name,
                "start_point": {"row": node.start_point[0], "column": node.start_point[1]},
                "end_point": {"row": node.end_point[0], "column": node.end_point[1]},
                "id": node.id,
            }

        focus = self._build_ast(target, code, max_depth=max_depth)

        # Build ancestor chain
        ancestors: List[Dict[str, Any]] = []
        parent = target.parent
        child = target
        while parent:
            ancestors.append(to_summary(parent, parent.parent if parent.parent else None))
            child = parent
            parent = parent.parent
        ancestors.reverse()

        # Sibling snapshots
        prev_sibling = target.prev_sibling
        next_sibling = target.next_sibling

        siblings = {
            "previous": to_summary(prev_sibling, target.parent) if prev_sibling else None,
            "next": to_summary(next_sibling, target.parent) if next_sibling else None,
        }

        # Direct children (shallow summaries)
        children_summaries = [
            to_summary(child_node, target)
            for child_node in target.children
        ]

        return {
            "focus": focus.model_dump(),
            "ancestors": ancestors,
            "siblings": siblings,
            "children": children_summaries,
        }

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
