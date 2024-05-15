from langchain.graphs import Neo4jGraph

from config import config


graph = Neo4jGraph(
    url=config.neo4j_url,
    username=config.neo4j_username,
    password=config.neo4j_password
)
