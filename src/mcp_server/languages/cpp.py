from typing import List
from tree_sitter import Node, Query, QueryCursor
from ..core.analyzer import BaseAnalyzer
from ..core.models import Symbol, Point, CallGraph, CallGraphNode, SearchResult

class CppAnalyzer(BaseAnalyzer):
    def get_language_name(self) -> str:
        return 'cpp'

    def extract_symbols(self, root_node: Node, file_path: str) -> List[Symbol]:
        symbols = []
        language = self.language_manager.get_language('cpp')
        
        query_scm = """
        (function_definition
          declarator: (function_declarator
            declarator: (identifier) @function.name)) @function.def
        (class_specifier
          name: (type_identifier) @class.name) @class.def
        """
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)
        
        for capture_name, nodes in captures.items():
            for node in nodes:
                if capture_name == 'function.def':
                    declarator = node.child_by_field_name('declarator')
                    while declarator and declarator.type in ('pointer_declarator', 'function_declarator', 'parenthesized_declarator', 'reference_declarator'):
                         declarator = declarator.child_by_field_name('declarator')
                    
                    if declarator and (declarator.type == 'identifier' or declarator.type == 'field_identifier'):
                        name = declarator.text.decode('utf8')
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
        nodes = []
        language = self.language_manager.get_language('cpp')
        
        func_query_scm = """
        (function_definition
          declarator: (function_declarator
            declarator: (identifier) @function.name)) @function.def
        """
        func_query = Query(language, func_query_scm)
        func_cursor = QueryCursor(func_query)
        func_captures = func_cursor.captures(root_node)
        
        for func_capture_name, func_nodes in func_captures.items():
            for func_node in func_nodes:
                if func_capture_name == 'function.def':
                    declarator = func_node.child_by_field_name('declarator')
                    while declarator and declarator.type in ('pointer_declarator', 'function_declarator', 'parenthesized_declarator', 'reference_declarator'):
                         declarator = declarator.child_by_field_name('declarator')
                    
                    if not declarator or (declarator.type != 'identifier' and declarator.type != 'field_identifier'):
                        continue
                        
                    func_name = declarator.text.decode('utf8')
                    start = Point(row=func_node.start_point[0], column=func_node.start_point[1])
                    end = Point(row=func_node.end_point[0], column=func_node.end_point[1])
                    
                    calls = []
                    call_query_scm = """
                    (call_expression
                      function: (identifier) @call.name)
                    (call_expression
                      function: (field_expression
                        field: (field_identifier) @call.method))
                    """
                    call_query = Query(language, call_query_scm)
                    call_cursor = QueryCursor(call_query)
                    call_captures = call_cursor.captures(func_node)
                    
                    for call_capture_name, call_nodes in call_captures.items():
                        for call_node in call_nodes:
                            if call_capture_name == 'call.name':
                                calls.append(call_node.text.decode('utf8'))
                            elif call_capture_name == 'call.method':
                                calls.append(call_node.text.decode('utf8'))
                    
                    nodes.append(CallGraphNode(
                        name=func_name,
                        location={'start': start, 'end': end},
                        calls=calls
                    ))
                
        return CallGraph(nodes=nodes)

    def find_function(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        matches = []
        language = self.language_manager.get_language('cpp')
        
        query_scm = """
        (function_definition
          declarator: (function_declarator
            declarator: (identifier) @function.name
            (#eq? @function.name "{name}"))) @function.def
        """.format(name=name)
        
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)
        
        for capture_name, nodes in captures.items():
            for node in nodes:
                if capture_name == 'function.def':
                    start = Point(row=node.start_point[0], column=node.start_point[1])
                    end = Point(row=node.end_point[0], column=node.end_point[1])
                    matches.append(Symbol(name=name, kind='function', location={'start': start, 'end': end}, file_path=file_path))
                
        return SearchResult(query=name, matches=matches)

    def find_variable(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        matches = []
        language = self.language_manager.get_language('cpp')
        
        query_scm = """
        (declaration
          declarator: (init_declarator
            declarator: (identifier) @var.name
            (#eq? @var.name "{name}"))) @var.def
            
        (declaration
          declarator: (identifier) @var.name
          (#eq? @var.name "{name}")) @var.def
          
        (assignment_expression
          left: (identifier) @var.name
          (#eq? @var.name "{name}")) @var.use
        """.format(name=name)
        
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)
        
        for capture_name, nodes in captures.items():
            for node in nodes:
                kind = 'variable_def' if 'def' in capture_name else 'variable_use'
                start = Point(row=node.start_point[0], column=node.start_point[1])
                end = Point(row=node.end_point[0], column=node.end_point[1])
                matches.append(Symbol(name=name, kind=kind, location={'start': start, 'end': end}, file_path=file_path))
                
        return SearchResult(query=name, matches=matches)

    def find_usage(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        matches = []
        language = self.language_manager.get_language('cpp')
        
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
        language = self.language_manager.get_language('cpp')
        
        query_scm = """
        (preproc_include
          path: (_) @path)
        """
        
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)
        
        for capture_name, nodes in captures.items():
            for node in nodes:
                text = node.text.decode('utf8')
                # Remove quotes or brackets
                if text.startswith('"') and text.endswith('"'):
                    dependencies.append(text[1:-1])
                elif text.startswith('<') and text.endswith('>'):
                    dependencies.append(text[1:-1])
                else:
                    dependencies.append(text)
                
        return dependencies
