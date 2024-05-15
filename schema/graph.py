from typing import List, Optional

from pydantic import Field
from langchain.pydantic_v1 import Field, BaseModel
from langchain_community.graphs.graph_document import (
    Node as BaseNode,
    Relationship as BaseRelationship,
)

class Property(BaseModel):
  key: str = Field(..., description="key")
  value: str = Field(..., description="value")

class Node(BaseNode):
    properties: Optional[List[Property]] = Field(None, description="List of node properties")

class Relationship(BaseRelationship):
    properties: Optional[List[Property]] = Field(None, description="List of relationship properties")

class KnowledgeGraph(BaseModel):
    nodes: List[Node] = Field(..., description="List of nodes in the knowledge graph")
    rels: List[Relationship] = Field(..., description="List of relationships in the knowledge graph")
