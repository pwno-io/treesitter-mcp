from typing import List
from tree_sitter import Node, Query, QueryCursor
from ..core.analyzer import BaseAnalyzer
from ..core.models import Symbol, Point, CallGraph, CallGraphNode, SearchResult

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
        """Build a call graph showing which functions call which other functions."""
        nodes = []
        language = self.language_manager.get_language('python')

        # Find all function definitions
        func_query_scm = """
        (function_definition
          name: (identifier) @function.name) @function.def
        """
        func_query = Query(language, func_query_scm)
        func_cursor = QueryCursor(func_query)
        func_captures = func_cursor.captures(root_node)

        if 'function.def' in func_captures:
            for func_node in func_captures['function.def']:
                # Extract function name
                name_node = func_node.child_by_field_name('name')
                if not name_node:
                    continue

                func_name = name_node.text.decode('utf8')
                start = Point(row=func_node.start_point[0], column=func_node.start_point[1])
                end = Point(row=func_node.end_point[0], column=func_node.end_point[1])

                # Find calls inside this function
                calls = []
                call_query_scm = """
                (call
                  function: (identifier) @call.name)
                """
                call_query = Query(language, call_query_scm)
                call_cursor = QueryCursor(call_query)
                call_captures = call_cursor.captures(func_node)

                if 'call.name' in call_captures:
                    for call_node in call_captures['call.name']:
                        calls.append(call_node.text.decode('utf8'))

                nodes.append(CallGraphNode(
                    name=func_name,
                    location={'start': start, 'end': end},
                    calls=calls
                ))

        return CallGraph(nodes=nodes)

    def find_function(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        """Find functions by name."""
        matches = []
        language = self.language_manager.get_language('python')

        query_scm = """
        (function_definition
          name: (identifier) @function.name
          (#eq? @function.name "{name}")) @function.def
        """.format(name=name)

        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        if 'function.def' in captures:
            for node in captures['function.def']:
                start = Point(row=node.start_point[0], column=node.start_point[1])
                end = Point(row=node.end_point[0], column=node.end_point[1])
                matches.append(Symbol(name=name, kind='function', location={'start': start, 'end': end}, file_path=file_path))

        return SearchResult(query=name, matches=matches)

    def find_variable(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        """Find variable definitions and usages."""
        matches = []
        language = self.language_manager.get_language('python')

        # Search for assignments and identifiers
        query_scm = """
        (assignment
          left: (identifier) @var.name
          (#eq? @var.name "{name}")) @var.def

        (identifier) @identifier
        (#eq? @identifier "{name}")
        """.format(name=name)

        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        for capture_name, nodes_list in captures.items():
            for node in nodes_list:
                kind = 'variable_def' if 'def' in capture_name else 'variable_use'
                start = Point(row=node.start_point[0], column=node.start_point[1])
                end = Point(row=node.end_point[0], column=node.end_point[1])
                matches.append(Symbol(name=name, kind=kind, location={'start': start, 'end': end}, file_path=file_path))

        return SearchResult(query=name, matches=matches)

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
