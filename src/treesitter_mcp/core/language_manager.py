import tree_sitter_c
import tree_sitter_cpp
import tree_sitter_javascript
import tree_sitter_php
import tree_sitter_rust
import tree_sitter_typescript
import tree_sitter_go
import tree_sitter_java
import tree_sitter_python
from tree_sitter import Language, Parser

class LanguageManager:
    """Manages Tree-sitter languages and parsers."""
    def __init__(self):
        """Initialize supported languages (C, C++, Python)."""
        self._languages = {
            'c': Language(tree_sitter_c.language()),
            'cpp': Language(tree_sitter_cpp.language()),
            'javascript': Language(tree_sitter_javascript.language()),
            'php': Language(tree_sitter_php.language_php()),
            'rust': Language(tree_sitter_rust.language()),
            'typescript': Language(tree_sitter_typescript.language_typescript()),
            'go': Language(tree_sitter_go.language()),
            'java': Language(tree_sitter_java.language()),
            'python': Language(tree_sitter_python.language()),
        }
        self._parsers = {}

    def get_language(self, language_name: str) -> Language:
        """Get the Tree-sitter Language object for a given name."""
        if language_name not in self._languages:
            raise ValueError(f"Language {language_name} not supported")
        return self._languages[language_name]

    def get_parser(self, language_name: str) -> Parser:
        """Get (or create) a Tree-sitter Parser for a given language."""
        if language_name not in self._parsers:
            parser = Parser(self.get_language(language_name))
            self._parsers[language_name] = parser
        return self._parsers[language_name]
