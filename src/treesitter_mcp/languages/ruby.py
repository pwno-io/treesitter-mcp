from typing import List
from tree_sitter import Node, Query, QueryCursor
from ..core.analyzer import BaseAnalyzer
from ..core.models import Symbol, Point, CallGraph, CallGraphNode, SearchResult


class RubyAnalyzer(BaseAnalyzer):
    def get_language_name(self) -> str:
        return 'ruby'

    def extract_symbols(self, root_node: Node, file_path: str) -> List[Symbol]:
        symbols = []
        language = self.language_manager.get_language('ruby')

        # Query for methods and classes
        query_scm = """
        (method
          name: (identifier) @method.name) @method.def
        (class
          name: (constant) @class.name) @class.def
        (module
          name: (constant) @module.name) @module.def
        (singleton_method
          name: (identifier) @singleton_method.name) @singleton_method.def
        """
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        for capture_name, nodes in captures.items():
            for node in nodes:
                if capture_name == 'method.def':
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        name = name_node.text.decode('utf8')
                        start = Point(row=node.start_point[0], column=node.start_point[1])
                        end = Point(row=node.end_point[0], column=node.end_point[1])
                        symbols.append(Symbol(name=name, kind='method', location={'start': start, 'end': end}, file_path=file_path))

                elif capture_name == 'class.def':
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        name = name_node.text.decode('utf8')
                        start = Point(row=node.start_point[0], column=node.start_point[1])
                        end = Point(row=node.end_point[0], column=node.end_point[1])
                        symbols.append(Symbol(name=name, kind='class', location={'start': start, 'end': end}, file_path=file_path))

                elif capture_name == 'module.def':
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        name = name_node.text.decode('utf8')
                        start = Point(row=node.start_point[0], column=node.start_point[1])
                        end = Point(row=node.end_point[0], column=node.end_point[1])
                        symbols.append(Symbol(name=name, kind='module', location={'start': start, 'end': end}, file_path=file_path))

                elif capture_name == 'singleton_method.def':
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        name = name_node.text.decode('utf8')
                        start = Point(row=node.start_point[0], column=node.start_point[1])
                        end = Point(row=node.end_point[0], column=node.end_point[1])
                        symbols.append(Symbol(name=name, kind='singleton_method', location={'start': start, 'end': end}, file_path=file_path))

        return symbols

    def get_call_graph(self, root_node: Node, file_path: str) -> CallGraph:
        """Build a call graph showing which methods call which other methods."""
        nodes = []
        language = self.language_manager.get_language('ruby')

        # First, find all method definitions
        method_names = set()
        method_query_scm = """
        (method
          name: (identifier) @method.name)
        (singleton_method
          name: (identifier) @singleton_method.name)
        """
        method_query = Query(language, method_query_scm)
        method_cursor = QueryCursor(method_query)
        method_captures = method_cursor.captures(root_node)

        for capture_name, method_nodes in method_captures.items():
            for node in method_nodes:
                method_names.add(node.text.decode('utf8'))

        # Find all method definitions and their calls
        func_query_scm = """
        (method
          name: (identifier) @method.name) @method.def
        (singleton_method
          name: (identifier) @method.name) @singleton_method.def
        """
        func_query = Query(language, func_query_scm)
        func_cursor = QueryCursor(func_query)
        func_captures = func_cursor.captures(root_node)

        for capture_name, func_nodes in func_captures.items():
            for func_node in func_nodes:
                name_node = func_node.child_by_field_name('name')
                if not name_node:
                    continue

                func_name = name_node.text.decode('utf8')
                start = Point(row=func_node.start_point[0], column=func_node.start_point[1])
                end = Point(row=func_node.end_point[0], column=func_node.end_point[1])

                calls = []
                # Find calls within this method
                # In Ruby, bare identifiers are indistinguishable from variables in AST
                # So we only detect explicit calls (with parentheses or arguments)
                call_query_scm = """
                (call
                  method: (identifier) @call.name)
                """
                call_query = Query(language, call_query_scm)
                call_cursor = QueryCursor(call_query)
                call_captures = call_cursor.captures(func_node)

                for call_capture_name, call_nodes in call_captures.items():
                    for call_node in call_nodes:
                        call_name = call_node.text.decode('utf8')
                        if call_name in method_names:
                            calls.append(call_name)

                # Also look for identifiers that might be method calls
                # This is a heuristic - identifiers that aren't local variables
                # might be method calls
                identifier_query_scm = """
                (identifier) @id
                """
                identifier_query = Query(language, identifier_query_scm)
                identifier_cursor = QueryCursor(identifier_query)
                identifier_captures = identifier_cursor.captures(func_node)

                # Track identifiers that are part of assignments (likely variables)
                var_defs = set()
                for id_capture_name, id_nodes in identifier_captures.items():
                    for id_node in id_nodes:
                        parent = id_node.parent
                        if parent and parent.type == 'assignment':
                            left = parent.child_by_field_name('left')
                            if left and id_node == left:
                                var_defs.add(id_node.text.decode('utf8'))

                # Add identifiers that aren't variables and are known methods
                for id_capture_name, id_nodes in identifier_captures.items():
                    for id_node in id_nodes:
                        id_name = id_node.text.decode('utf8')
                        # Skip if it's a variable definition
                        if id_name in var_defs:
                            continue
                        # Skip if it's the method name itself
                        if id_name == func_name:
                            continue
                        # Add if it's a known method
                        if id_name in method_names and id_name not in calls:
                            calls.append(id_name)

                nodes.append(CallGraphNode(
                    name=func_name,
                    location={'start': start, 'end': end},
                    calls=calls
                ))

        return CallGraph(nodes=nodes)

    def find_function(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        """Find methods by name."""
        matches = []
        language = self.language_manager.get_language('ruby')

        query_scm = """
        (method
          name: (identifier) @method.name
          (#eq? @method.name "{name}")) @method.def
        (singleton_method
          name: (identifier) @method.name
          (#eq? @method.name "{name}")) @singleton_method.def
        """.format(name=name)

        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        for capture_name, nodes in captures.items():
            for node in nodes:
                start = Point(row=node.start_point[0], column=node.start_point[1])
                end = Point(row=node.end_point[0], column=node.end_point[1])
                matches.append(Symbol(name=name, kind='function', location={'start': start, 'end': end}, file_path=file_path))

        return SearchResult(query=name, matches=matches)

    def find_variable(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        """Find variable definitions and usages."""
        matches = []
        language = self.language_manager.get_language('ruby')

        # Check if this is an instance variable (starts with @)
        is_instance_var = name.startswith('@')

        if is_instance_var:
            # For instance variables, match them directly
            query_scm = """
            (assignment
              left: (instance_variable) @var.left)
            (instance_variable) @instance_var
            """
        else:
            # For regular variables
            query_scm = """
            (assignment
              left: (_) @var.left
              right: (_) @var.right)
            (identifier) @identifier
            """

        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        # Track assignments to identify defs vs uses
        assignments = {}
        for capture_name, nodes in captures.items():
            for node in nodes:
                if capture_name == 'var.left':
                    var_name = node.text.decode('utf8')
                    if var_name not in assignments:
                        assignments[var_name] = []
                    assignments[var_name].append(('def', node))

        # Now collect all matching variables
        for capture_name, nodes in captures.items():
            for node in nodes:
                if capture_name in ['identifier', 'instance_var']:
                    var_name = node.text.decode('utf8')
                    if var_name == name:
                        # Check if this is a definition
                        kind = 'variable_use'
                        if var_name in assignments:
                            for def_kind, def_node in assignments[var_name]:
                                if node == def_node:
                                    kind = 'variable_def'
                                    break

                        start = Point(row=node.start_point[0], column=node.start_point[1])
                        end = Point(row=node.end_point[0], column=node.end_point[1])
                        matches.append(Symbol(name=name, kind=kind, location={'start': start, 'end': end}, file_path=file_path))

        return SearchResult(query=name, matches=matches)

    def find_usage(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        """Find all usages of an identifier."""
        matches = []
        language = self.language_manager.get_language('ruby')

        query_scm = """
        (identifier) @usage
        (constant) @usage
        """

        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        for capture_name, nodes in captures.items():
            for node in nodes:
                text = node.text.decode('utf8')
                if text == name:
                    start = Point(row=node.start_point[0], column=node.start_point[1])
                    end = Point(row=node.end_point[0], column=node.end_point[1])
                    matches.append(Symbol(name=name, kind='usage', location={'start': start, 'end': end}, file_path=file_path))

        return SearchResult(query=name, matches=matches)

    def get_dependencies(self, root_node: Node, file_path: str) -> List[str]:
        """Extract dependencies from require and require_relative statements."""
        dependencies = []
        language = self.language_manager.get_language('ruby')

        # Find all call nodes
        query_scm = """
        (call) @call
        """

        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        for capture_name, nodes in captures.items():
            for call_node in nodes:
                # Get the method name
                method_node = call_node.child_by_field_name('method')
                if not method_node or method_node.type != 'identifier':
                    continue

                method_name = method_node.text.decode('utf8')
                if method_name not in ['require', 'require_relative', 'gem']:
                    continue

                # Get the argument list
                args_node = call_node.child_by_field_name('arguments')
                if not args_node or args_node.type != 'argument_list':
                    continue

                # Find string arguments
                for child in args_node.children:
                    if child.type == 'string':
                        text = child.text.decode('utf8')
                        # Remove quotes
                        if len(text) >= 2 and text[0] in ('"', "'"):
                            text = text[1:-1]
                        dependencies.append(text)

        return dependencies
