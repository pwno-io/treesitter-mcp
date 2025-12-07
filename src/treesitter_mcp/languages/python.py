from typing import List
from tree_sitter import Node, Query, QueryCursor
from ..core.analyzer import BaseAnalyzer
from ..core.models import Symbol, Point, CallGraph, SearchResult

class PythonAnalyzer(BaseAnalyzer):
    def get_language_name(self) -> str:
        return 'python'

    def extract_symbols(self, root_node: Node, file_path: str) -> List[Symbol]:
        symbols = []
        language = self.language_manager.get_language('python')
        
        # Query for functions and classes
        query_scm = """
        (function_definition
          name: (identifier) @function.name) @function.def
        (class_definition
          name: (identifier) @class.name) @class.def
        """
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)
        
        for capture_name, nodes in captures.items():
            for node in nodes:
                if capture_name == 'function.def':
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        name = name_node.text.decode('utf8')
                        start = Point(row=node.start_point[0], column=node.start_point[1])
                        end = Point(row=node.end_point[0], column=node.end_point[1])
                        symbols.append(Symbol(name=name, kind='function', location={'start': start, 'end': end}, file_path=file_path))

                elif capture_name == 'class.def':
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        name = name_node.text.decode('utf8')
                        start = Point(row=node.start_point[0], column=node.start_point[1])
                        end = Point(row=node.end_point[0], column=node.end_point[1])
                        symbols.append(Symbol(name=name, kind='class', location={'start': start, 'end': end}, file_path=file_path))
            
        return symbols

    def get_call_graph(self, root_node: Node, file_path: str) -> CallGraph:
        # Placeholder for Python call graph
        return CallGraph(nodes=[])

    def find_function(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        # Placeholder for Python function search
        return SearchResult(query=name, matches=[])

    def find_variable(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        # Placeholder for Python variable search
        return SearchResult(query=name, matches=[])

    def find_usage(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        matches = []
        language = self.language_manager.get_language('python')
        
        query_scm = """
        (identifier) @usage
        """
        
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)
        
        for capture_name, nodes in captures.items():
            for node in nodes:
                if node.text.decode('utf8') != name:
                    continue
                start = Point(row=node.start_point[0], column=node.start_point[1])
                end = Point(row=node.end_point[0], column=node.end_point[1])
                matches.append(Symbol(name=name, kind='usage', location={'start': start, 'end': end}, file_path=file_path))
                
        return SearchResult(query=name, matches=matches)

    def get_dependencies(self, root_node: Node, file_path: str) -> List[str]:
        dependencies = []
        language = self.language_manager.get_language('python')
        
        query_scm = """
        (import_statement
          name: (dotted_name) @import)
        (import_statement
          name: (aliased_import
            name: (dotted_name) @import))
        (import_from_statement
          module_name: (dotted_name) @import)
        """
        
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)
        
        for capture_name, nodes in captures.items():
            for node in nodes:
                dependencies.append(node.text.decode('utf8'))
                
        return dependencies
