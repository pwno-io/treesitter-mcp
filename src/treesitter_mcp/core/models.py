from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Point(BaseModel):
    """Represents a point in source code (row, column)."""
    row: int
    column: int

class ASTNode(BaseModel):
    """Represents a node in the Abstract Syntax Tree."""
    type: str
    start_point: Point
    end_point: Point
    children: List['ASTNode'] = Field(default_factory=list)
    text: Optional[str] = None
    id: Optional[int] = None

class Symbol(BaseModel):
    """Represents an extracted symbol (function, class, variable)."""
    name: str
    kind: str
    location: Dict[str, Point]
    file_path: str

class AnalysisResult(BaseModel):
    """Result of a comprehensive file analysis."""
    file_path: str
    language: str
    ast: ASTNode
    symbols: List[Symbol]
    errors: List[str] = Field(default_factory=list)

class CallGraphNode(BaseModel):
    """Node in a call graph representing a function and its calls."""
    name: str
    location: Dict[str, Point]
    calls: List[str] = Field(default_factory=list)

class CallGraph(BaseModel):
    """Represents the call graph of a file."""
    nodes: List[CallGraphNode]

class SearchResult(BaseModel):
    """Result of a search operation."""
    query: str
    matches: List[Symbol]

ASTNode.model_rebuild()
