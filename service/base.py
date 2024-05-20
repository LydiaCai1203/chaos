from typing import Optional, List

from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_community.graphs.graph_document import (
    Node as BaseNode,
    Relationship as BaseRelationship,
)
from db.neo4j import driver
from schema.graph import KnowledgeGraph, Node, Relationship


llm = ChatOpenAI(
    streaming=True,
    verbose=True,
    callbacks=[],
    model_name="moonshot-v1-8k",
    openai_api_base="https://api.moonshot.cn/v1",
    openai_api_key="sk-z8KWnfxLSLiHmrX0XvG34qnQaH2Wm617dUBzqfAOABozb1HJ",
    openai_proxy="",
    temperature=0.7,
    max_tokens=1000,
)

def props_to_dict(props) -> dict:
    """ 把属性和属性值构造成 dict
    """
    properties = {}
    if not props:
      return properties
    for p in props:
        properties[p.key] = p.value
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

def get_prompt_template(
    allowed_nodes: Optional[List[str]] = None,
    allowed_rels: Optional[List[str]] = None
):
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
                # 知识图谱介绍
                ## 1. 概览
                    您是一种顶级算法，旨在以结构化格式提取信息以构建知识图。
                    - **节点**代表实体和概念。它们类似于维基百科节点。
                    - 目的是实现知识图谱的简单性和清晰度，使其可供广大受众使用。
                ## 2. 标签节点
                    - **一致性**：确保使用基本或基本类型作为节点标签。
                    - 例如，当您识别代表一个人的实体时，请始终将其标记为**“人”**。避免使用“数学家”或“科学家”等更具体的术语。
                    - **节点 ID**：切勿使用整数作为节点 ID。节点 ID 应该是文本中的名称或人类可读的标识符。
                    {'- **允许使用的节点标签**:' + ", ".join(allowed_nodes) if allowed_nodes else ""}
                    {'- **允许使用的关系类型**:' + ", ".join(allowed_rels) if allowed_rels else ""}
                ## 3. 处理数字数据和日期
                    - 数字数据，如年龄或其他相关信息，应作为相应节点的属性或特性合并。
                    - **没有日期/数字的单独节点**：不要为日期或数值创建单独的节点。始终将它们附加为节点的属性或属性。
                    - **属性格式**：属性必须采用键值格式。
                    - **引号**：切勿在属性值中使用转义单引号或双引号。
                ## 4. 共指解析
                    - **维护实体一致性**：提取实体时，确保一致性至关重要。
                    如果某个实体（例如“John Doe”）在文本中多次提及，但使用不同的名称或代词（例如“Joe”、“he”），
                    在整个知识图中始终使用该实体最完整的标识符。在此示例中，使用“John Doe”作为实体 ID。
                    请记住，知识图应该是连贯且易于理解的，因此保持实体引用的一致性至关重要。
                ## 5. 严格合规
                    严格遵守规则。不遵守规定将导致终止。
                """
            ),
            ("system", "输出格式：{format}"),
            ("human", "使用给定的格式从以下输入中提取信息：{input}"),
            ("human", "提示：确保输出格式按照规则，不要输出其他无关的文字"),
        ])

def extract_and_store_graph(
    document: Document,
    nodes:Optional[List[str]] = None,
    rels:Optional[List[str]]=None
) -> None:
    prompt = get_prompt_template()
    output_parser = PydanticOutputParser(pydantic_object=KnowledgeGraph)
    format_instructions = output_parser.get_format_instructions()
    chain = prompt | llm | output_parser
    kg = chain.invoke({"input": document.page_content, "format": format_instructions})
