# Tree-sitter MCP Server

An MCP server that uses Tree-sitter to parse and analyze code. Works with 10 languages: C, C++, Python, JavaScript, TypeScript, Go, Java, PHP, Rust, and Ruby.

## What it does

- Parse files and get their AST
- Extract functions and variables
- Build call graphs
- Find where functions/variables are used
- Run custom Tree-sitter queries
- List imports/includes

## Install

Requires Python 3.10+.

```bash
# Clone and install
git clone <repo-url>
cd treesitter-mcp

# With uv (faster)
uv pip install -e .

# Or with pip
pip install -e .
```

Or run without installing:
```bash
uvx treesitter-mcp
```

## Running

### As an MCP server (default)
For use with Claude Desktop or other MCP clients:
```bash
treesitter-mcp
```

See `docs/MCP_USAGE.md` for how to configure.

### HTTP mode
For testing or manual use:
```bash
treesitter-mcp --http --port 8000 --host 127.0.0.1
```

### Limiting tools
Only expose certain tools with `--tools`:
```bash
treesitter-mcp --http --port 8000 --tools treesitter_analyze_file,treesitter_get_ast
```

Or via URL query param: `http://127.0.0.1:8000?tools=treesitter_analyze_file,treesitter_get_ast`

Tools available:
- `treesitter_analyze_file` - Basic analysis
- `treesitter_get_ast` - Full AST
- `treesitter_get_call_graph` - Function calls
- `treesitter_find_function` - Find function definitions
- `treesitter_find_variable` - Find variables
- `treesitter_get_supported_languages` - What's supported
- `treesitter_get_node_at_point` - AST node at a line/column
- `treesitter_get_node_for_range` - AST node for a range
- `treesitter_cursor_walk` - Walk tree with context
- `treesitter_run_query` - Custom Tree-sitter queries
- `treesitter_find_usage` - Find symbol usages
- `treesitter_get_dependencies` - Extract imports/includes

If you don't specify `--tools`, everything is exposed.

## Language support

| Language | analyze_file | get_ast | get_call_graph | find_function | find_variable | find_usage | get_dependencies |
|----------|--------------|---------|----------------|---------------|---------------|------------|------------------|
| C        | ✅          | ✅     | ✅            | ✅           | ✅           | ✅        | ✅              |
| C++      | ✅          | ✅     | ✅            | ✅           | ✅           | ✅        | ✅              |
| Python   | ✅          | ✅     | ✅            | ✅           | ✅           | ✅        | ✅              |
| JavaScript | ✅        | ✅     | ✅            | ✅           | ✅           | ✅        | ✅              |
| TypeScript | ✅        | ✅     | ✅            | ✅           | ✅           | ✅        | ✅              |
| Go       | ✅          | ✅     | ✅            | ✅           | ✅           | ✅        | ✅              |
| Java     | ✅          | ✅     | ✅            | ✅           | ✅           | ✅        | ✅              |
| PHP      | ✅          | ✅     | ✅            | ✅           | ✅           | ✅        | ✅              |
| Rust     | ✅          | ✅     | ✅            | ✅           | ✅           | ✅        | ✅              |
| Ruby     | ✅          | ✅     | ✅            | ✅           | ✅           | ✅        | ✅              |

### File extensions

| Language | Extensions |
|----------|------------|
| C        | `.c` |
| C++      | `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp` |
| Python   | `.py` |
| JavaScript | `.js`, `.jsx`, `.mjs`, `.cjs` |
| TypeScript | `.ts`, `.tsx`, `.cts`, `.mts` |
| Go       | `.go` |
| Java     | `.java` |
| PHP      | `.php`, `.phtml` |
| Rust     | `.rs` |
| Ruby     | `.rb` |

## Docs

- [API Reference](docs/API.md)
- [MCP Server Usage](docs/MCP_USAGE.md)
- [Architecture](docs/ARCHITECTURE.md)
