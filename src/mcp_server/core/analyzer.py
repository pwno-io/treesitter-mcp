from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from tree_sitter import Node, Tree
from .models import AnalysisResult, ASTNode, Point, Symbol, CallGraph, SearchResult

class BaseAnalyzer(ABC):
    def __init__(self, language_manager):
        self.language_manager = language_manager

    @abstractmethod
    def get_language_name(self) -> str:
        pass

    def parse(self, code: str) -> Tree:
        parser = self.language_manager.get_parser(self.get_language_name())
        return parser.parse(bytes(code, "utf8"))

    def analyze(self, file_path: str, code: str) -> AnalysisResult:
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
        start = Point(row=node.start_point[0], column=node.start_point[1])
        end = Point(row=node.end_point[0], column=node.end_point[1])
        
        children = []
        if max_depth == -1 or depth < max_depth:
            children = [self._build_ast(child, code, depth + 1, max_depth) for child in node.children]
        
        text = None
        if not children:
             text = code[node.start_byte:node.end_byte]

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
        pass

    @abstractmethod
    def get_call_graph(self, root_node: Node, file_path: str) -> CallGraph:
        pass

    @abstractmethod
    def find_function(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        pass

    @abstractmethod
    def find_variable(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        pass

    @abstractmethod
    def find_usage(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        pass

    @abstractmethod
    def get_dependencies(self, root_node: Node, file_path: str) -> List[str]:
        pass

    def run_query(self, query_str: str, root_node: Node, code: str) -> List[Dict[str, Any]]:
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
                    
                    results.append({
                        "capture_name": capture_name,
                        "text": code[node.start_byte:node.end_byte],
                        "start": start.model_dump(),
                        "end": end.model_dump(),
                        "type": node.type
                    })
            return results
        except Exception as e:
            raise ValueError(f"Invalid query: {e}")
