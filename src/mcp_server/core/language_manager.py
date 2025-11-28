import tree_sitter_c
import tree_sitter_cpp
import tree_sitter_python
from tree_sitter import Language, Parser

class LanguageManager:
    def __init__(self):
        self._languages = {
            'c': Language(tree_sitter_c.language()),
            'cpp': Language(tree_sitter_cpp.language()),
            'python': Language(tree_sitter_python.language()),
        }
        self._parsers = {}

    def get_language(self, language_name: str) -> Language:
        if language_name not in self._languages:
            raise ValueError(f"Language {language_name} not supported")
        return self._languages[language_name]

    def get_parser(self, language_name: str) -> Parser:
        if language_name not in self._parsers:
            parser = Parser(self.get_language(language_name))
            self._parsers[language_name] = parser
        return self._parsers[language_name]
