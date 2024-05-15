import os
from typing import Optional, List

from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain
from langchain_community.graphs.graph_document import (
    GraphDocument,
    Node as BaseNode,
    Relationship as BaseRelationship,
)
from db.neo4j import graph
from schema.graph import KnowledgeGraph, Node, Relationship
from service.base import map_to_base_node, map_to_base_relationship

os.environ["OPENAI_API_KEY"] = "sk-"
llm = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0)

def format_property_key(s: str) -> str:
    """ 分词，首字母大写，针对英文
    """
    words = s.split()
    if not words:
        return s
    first_word = words[0].lower()
    capitalized_words = [word.capitalize() for word in words[1:]]
    return "".join([first_word] + capitalized_words)

def props_to_dict(props) -> dict:
    """ 把属性和属性值构造成 dict
    """
    properties = {}
    if not props:
      return properties
    for p in props:
        properties[format_property_key(p.key)] = p.value
    return properties

def map_to_base_node(node: Node) -> BaseNode:
    """ Node -> BaseNode
    """
    properties = props_to_dict(node.properties) if node.properties else {}
    properties["name"] = node.id.title()
    return BaseNode(
        id=node.id.title(), 
        type=node.type.capitalize(), 
        properties=properties
    )

def map_to_base_relationship(rel: Relationship) -> BaseRelationship:
    """ Relationship -> BaseRelationship
    """
    source = map_to_base_node(rel.source)
    target = map_to_base_node(rel.target)
    properties = props_to_dict(rel.properties) if rel.properties else {}
    return BaseRelationship(
        source=source, 
        target=target, 
        type=rel.type, 
        properties=properties
    )

def get_extraction_chain(
    allowed_nodes: Optional[List[str]] = None,
    allowed_rels: Optional[List[str]] = None
    ):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""# Knowledge Graph Instructions for GPT-4
                ## 1. Overview
                You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph.
                - **Nodes** represent entities and concepts. They're akin to Wikipedia nodes.
                - The aim is to achieve simplicity and clarity in the knowledge graph, making it accessible for a vast audience.
                ## 2. Labeling Nodes
                - **Consistency**: Ensure you use basic or elementary types for node labels.
                - For example, when you identify an entity representing a person, always label it as **"person"**. Avoid using more specific terms like "mathematician" or "scientist".
                - **Node IDs**: Never utilize integers as node IDs. Node IDs should be names or human-readable identifiers found in the text.
                {'- **Allowed Node Labels:**' + ", ".join(allowed_nodes) if allowed_nodes else ""}
                {'- **Allowed Relationship Types**:' + ", ".join(allowed_rels) if allowed_rels else ""}
                ## 3. Handling Numerical Data and Dates
                - Numerical data, like age or other related information, should be incorporated as attributes or properties of the respective nodes.
                - **No Separate Nodes for Dates/Numbers**: Do not create separate nodes for dates or numerical values. Always attach them as attributes or properties of nodes.
                - **Property Format**: Properties must be in a key-value format.
                - **Quotation Marks**: Never use escaped single or double quotes within property values.
                - **Naming Convention**: Use camelCase for property keys, e.g., `birthDate`.
                ## 4. Coreference Resolution
                - **Maintain Entity Consistency**: When extracting entities, it's vital to ensure consistency.
                If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"),
                always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID.
                Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.
                ## 5. Strict Compliance
                Adhere to the rules strictly. Non-compliance will result in termination.
                """
            ),
            ("human", "Use the given format to extract information from the following input: {input}"),
            ("human", "Tip: Make sure to answer in the correct format"),
        ])
    return create_structured_output_chain(KnowledgeGraph, llm, prompt, verbose=False)

def extract_and_store_graph(
    document: Document,
    nodes:Optional[List[str]] = None,
    rels:Optional[List[str]]=None) -> None:
    extract_chain = get_extraction_chain(nodes, rels)
    data = extract_chain.invoke(document.page_content)['function']
    graph_document = GraphDocument(
      nodes = [map_to_base_node(node) for node in data.nodes],
      relationships = [map_to_base_relationship(rel) for rel in data.rels],
      source = document
    )
    graph.add_graph_documents([graph_document])
