from typing import List
from tree_sitter import Node, Query, QueryCursor
from ..core.analyzer import BaseAnalyzer
from ..core.models import Symbol, Point, CallGraph, CallGraphNode, SearchResult


class GoAnalyzer(BaseAnalyzer):
    def get_language_name(self) -> str:
        return 'go'

    def extract_symbols(self, root_node: Node, file_path: str) -> List[Symbol]:
        symbols = []
        language = self.language_manager.get_language('go')

        query_scm = """
        (function_declaration
          name: (identifier) @function.name) @function.def
        (method_declaration
          name: (field_identifier) @method.name) @method.def
        (type_spec
          name: (type_identifier) @type.name
          type: (struct_type)) @struct.def
        (type_spec
          name: (type_identifier) @type.name
          type: (interface_type)) @interface.def
        """
        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        for capture_name, nodes in captures.items():
            for node in nodes:
                name_node = node.child_by_field_name('name')
                if not name_node:
                    continue

                name = name_node.text.decode('utf8')
                start = Point(row=node.start_point[0], column=node.start_point[1])
                end = Point(row=node.end_point[0], column=node.end_point[1])

                if capture_name == 'function.def':
                    kind = 'function'
                elif capture_name == 'method.def':
                    kind = 'method'
                elif capture_name == 'struct.def':
                    kind = 'struct'
                elif capture_name == 'interface.def':
                    kind = 'interface'
                else:
                    continue

                symbols.append(Symbol(name=name, kind=kind, location={'start': start, 'end': end}, file_path=file_path))

        return symbols

    def get_call_graph(self, root_node: Node, file_path: str) -> CallGraph:
        nodes = []
        language = self.language_manager.get_language('go')

        func_query_scm = """
        (function_declaration
          name: (identifier) @function.name) @function.def
        (method_declaration
          name: (field_identifier) @method.name) @method.def
        """
        func_query = Query(language, func_query_scm)
        func_cursor = QueryCursor(func_query)
        func_captures = func_cursor.captures(root_node)

        for _, func_nodes in func_captures.items():
            for func_node in func_nodes:
                name_node = func_node.child_by_field_name('name')
                if not name_node:
                    continue

                func_name = name_node.text.decode('utf8')
                start = Point(row=func_node.start_point[0], column=func_node.start_point[1])
                end = Point(row=func_node.end_point[0], column=func_node.end_point[1])

                calls = []
                call_query_scm = """
                (call_expression
                  function: (identifier) @call.name)
                (call_expression
                  function: (selector_expression
                    field: (field_identifier) @call.method))
                """
                call_query = Query(language, call_query_scm)
                call_cursor = QueryCursor(call_query)
                call_captures = call_cursor.captures(func_node)

                for _, call_nodes in call_captures.items():
                    for call_node in call_nodes:
                        calls.append(call_node.text.decode('utf8'))

                nodes.append(CallGraphNode(
                    name=func_name,
                    location={'start': start, 'end': end},
                    calls=calls
                ))

        return CallGraph(nodes=nodes)

    def find_function(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        matches = []
        language = self.language_manager.get_language('go')

        query_scm = """
        (function_declaration
          name: (identifier) @function.name
          (#eq? @function.name "{name}")) @function.def
        (method_declaration
          name: (field_identifier) @method.name
          (#eq? @method.name "{name}")) @method.def
        """.format(name=name)

        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        for _, nodes in captures.items():
            for node in nodes:
                start = Point(row=node.start_point[0], column=node.start_point[1])
                end = Point(row=node.end_point[0], column=node.end_point[1])
                matches.append(Symbol(name=name, kind='function', location={'start': start, 'end': end}, file_path=file_path))

        return SearchResult(query=name, matches=matches)

    def find_variable(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        matches = []
        language = self.language_manager.get_language('go')

        query_scm = """
        (short_var_declaration
          left: (expression_list
            (identifier) @var.name)
          (#eq? @var.name "{name}")) @var.def

        (var_spec
          (identifier) @var.name
          (#eq? @var.name "{name}")) @var.def
        (var_spec
          (identifier) @var.name
          (identifier) @var.name
          (#eq? @var.name "{name}")) @var.def

        (assignment_statement
          left: (expression_list
            (identifier) @var.name)
          (#eq? @var.name "{name}")) @var.use

        (identifier) @var.use
        """
        query = Query(language, query_scm.format(name=name))
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        for capture_name, nodes in captures.items():
            for node in nodes:
                text = node.text.decode('utf8')
                if capture_name == 'var.use' and text != name:
                    continue
                kind = 'variable_def' if 'def' in capture_name else 'variable_use'
                start = Point(row=node.start_point[0], column=node.start_point[1])
                end = Point(row=node.end_point[0], column=node.end_point[1])
                matches.append(Symbol(name=text, kind=kind, location={'start': start, 'end': end}, file_path=file_path))

        return SearchResult(query=name, matches=matches)

    def find_usage(self, root_node: Node, file_path: str, name: str) -> SearchResult:
        matches = []
        language = self.language_manager.get_language('go')

        query_scm = """
        (identifier) @usage
        """

        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        for _, nodes in captures.items():
            for node in nodes:
                if node.text.decode('utf8') != name:
                    continue
                start = Point(row=node.start_point[0], column=node.start_point[1])
                end = Point(row=node.end_point[0], column=node.end_point[1])
                matches.append(Symbol(name=name, kind='usage', location={'start': start, 'end': end}, file_path=file_path))

        return SearchResult(query=name, matches=matches)

    def get_dependencies(self, root_node: Node, file_path: str) -> List[str]:
        dependencies = []
        language = self.language_manager.get_language('go')

        query_scm = """
        (import_spec
          path: (interpreted_string_literal) @path)
        (import_spec
          path: (raw_string_literal) @path)
        """

        query = Query(language, query_scm)
        cursor = QueryCursor(query)
        captures = cursor.captures(root_node)

        for _, nodes in captures.items():
            for node in nodes:
                text = node.text.decode('utf8')
                if text and text[0] in ('"', '`') and text[-1] == text[0]:
                    dependencies.append(text[1:-1])
                else:
                    dependencies.append(text)

        return dependencies

