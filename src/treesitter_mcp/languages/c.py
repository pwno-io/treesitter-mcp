from typing import List
from tree_sitter import Node, Query, QueryCursor
from ..core.analyzer import BaseAnalyzer
from ..core.models import Symbol, Point, CallGraph, CallGraphNode, SearchResult

class CAnalyzer(BaseAnalyzer):
    def get_language_name(self) -> str:
        return 'c'

    def extract_symbols(self, root_node: Node, file_path: str) -> List[Symbol]:
        symbols = []
        language = self.language_manager.get_language('c')
        
        query_scm = """
        (function_definition
          declarator: (function_declarator
            declarator: (identifier) @function.name)) @function.def
        (struct_specifier
          name: (type_identifier) @struct.name) @struct.def
        """
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)
        
        if 'function.def' in captures:
            for node in captures['function.def']:
                declarator = node.child_by_field_name('declarator')
                while declarator and declarator.type in ('pointer_declarator', 'function_declarator', 'parenthesized_declarator'):
                    if declarator.type == 'function_declarator':
                         declarator = declarator.child_by_field_name('declarator')
                    elif declarator.type == 'pointer_declarator':
                         declarator = declarator.child_by_field_name('declarator')
                    elif declarator.type == 'parenthesized_declarator':
                         declarator = declarator.child_by_field_name('declarator')
                
                if declarator and declarator.type == 'identifier':
                    name = declarator.text.decode('utf8')
                    start = Point(row=node.start_point[0], column=node.start_point[1])
                    end = Point(row=node.end_point[0], column=node.end_point[1])
                    symbols.append(Symbol(name=name, kind='function', location={'start': start, 'end': end}, file_path=file_path))

        if 'struct.def' in captures:
            for node in captures['struct.def']:
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = name_node.text.decode('utf8')
                    start = Point(row=node.start_point[0], column=node.start_point[1])
                    end = Point(row=node.end_point[0], column=node.end_point[1])
                    symbols.append(Symbol(name=name, kind='struct', location={'start': start, 'end': end}, file_path=file_path))

        return symbols

    def get_call_graph(self, root_node: Node, file_path: str) -> CallGraph:
        nodes = []
        language = self.language_manager.get_language('c')
        
        # Find all function definitions
        func_query_scm = """
        (function_definition
          declarator: (function_declarator
            declarator: (identifier) @function.name)) @function.def
        """
        func_query = Query(language, func_query_scm)
        func_cursor = QueryCursor(func_query)
        func_captures = func_cursor.captures(root_node)
        
        if 'function.def' in func_captures:
            for func_node in func_captures['function.def']:
                # Extract function name
                declarator = func_node.child_by_field_name('declarator')
                while declarator and declarator.type in ('pointer_declarator', 'function_declarator', 'parenthesized_declarator'):
                    if declarator.type == 'function_declarator':
                         declarator = declarator.child_by_field_name('declarator')
                    elif declarator.type == 'pointer_declarator':
                         declarator = declarator.child_by_field_name('declarator')
                    elif declarator.type == 'parenthesized_declarator':
                         declarator = declarator.child_by_field_name('declarator')
                
                if not declarator or declarator.type != 'identifier':
                    continue
                    
                func_name = declarator.text.decode('utf8')
                start = Point(row=func_node.start_point[0], column=func_node.start_point[1])
                end = Point(row=func_node.end_point[0], column=func_node.end_point[1])
                
                # Find calls inside this function
                calls = []
                call_query_scm = """
                (call_expression
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
        matches = []
        language = self.language_manager.get_language('c')
        
        query_scm = """
        (function_definition
          declarator: (function_declarator
            declarator: (identifier) @function.name
            (#eq? @function.name "{name}"))) @function.def
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
        matches = []
        language = self.language_manager.get_language('c')
        
        # Search for declarations and assignments
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
        
        for capture_name, nodes_list in captures.items():
            for node in nodes_list:
                kind = 'variable_def' if 'def' in capture_name else 'variable_use'
                start = Point(row=node.start_point[0], column=node.start_point[1])
                end = Point(row=node.end_point[0], column=node.end_point[1])
                matches.append(Symbol(name=name, kind=kind, location={'start': start, 'end': end}, file_path=file_path))
                
        return SearchResult(query=name, matches=matches)

    def find_usage(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        matches = []
        language = self.language_manager.get_language('c')
        
        query_scm = """
        (identifier) @usage
        """
        
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)
        
        if 'usage' in captures:
            for node in captures['usage']:
                if node.text.decode('utf8') != name:
                    continue
                start = Point(row=node.start_point[0], column=node.start_point[1])
                end = Point(row=node.end_point[0], column=node.end_point[1])
                matches.append(Symbol(name=name, kind='usage', location={'start': start, 'end': end}, file_path=file_path))
                
        return SearchResult(query=name, matches=matches)

    def get_dependencies(self, root_node: Node, file_path: str) -> List[str]:
        dependencies = []
        language = self.language_manager.get_language('c')
        
        query_scm = """
        (preproc_include
          path: (_) @path)
        """
        
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)
        
        if 'path' in captures:
            for node in captures['path']:
                text = node.text.decode('utf8')
                # Remove quotes or brackets
                if text.startswith('"') and text.endswith('"'):
                    dependencies.append(text[1:-1])
                elif text.startswith('<') and text.endswith('>'):
                    dependencies.append(text[1:-1])
                else:
                    dependencies.append(text)
                
        return dependencies
