from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Point(BaseModel):
    row: int
    column: int

class ASTNode(BaseModel):
    type: str
    start_point: Point
    end_point: Point
    children: List['ASTNode'] = Field(default_factory=list)
    text: Optional[str] = None
    id: Optional[int] = None

class Symbol(BaseModel):
    name: str
    kind: str
    location: Dict[str, Point]
    file_path: str

class AnalysisResult(BaseModel):
    file_path: str
    language: str
    ast: ASTNode
    symbols: List[Symbol]
    errors: List[str] = Field(default_factory=list)

class CallGraphNode(BaseModel):
    name: str
    location: Dict[str, Point]
    calls: List[str] = Field(default_factory=list)

class CallGraph(BaseModel):
    nodes: List[CallGraphNode]

class SearchResult(BaseModel):
    query: str
    matches: List[Symbol]

ASTNode.model_rebuild()
