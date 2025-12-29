"""Main entry point for treesitter-mcp.

This module runs the MCP server in stdio mode by default,
making it easy to use with uvx: `uvx treesitter-mcp`
"""
from ..server import main

if __name__ == "__main__":
    main()
