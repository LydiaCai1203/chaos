from typing import List, Optional, Union

from pydantic import Field
from langchain.pydantic_v1 import Field, BaseModel


class Property(BaseModel):
  key: str = Field(..., description="key")
  value: str = Field(..., description="value")

class Node(BaseModel):
    id: Union[str, int] = Field(None, description="A unique identifier for the node.")
    type: str = Field(None, description="The type or label of the node, default is “Node”.")
    properties: Optional[List[Property]] = Field(None, description="List of node properties")

class Relationship(BaseModel):
    properties: Optional[List[Property]] = Field(None, description="List of relationship properties")
    source: str = Field(..., description="The source node of the relationship.")
    target: str = Field(..., description="The target node of the relationship.")
    type: str = Field(..., description="The type of the relationship.")

class KnowledgeGraph(BaseModel):
    nodes: List[Node] = Field(..., description="List of nodes in the knowledge graph")
    rels: List[Relationship] = Field(..., description="List of relationships in the knowledge graph")
