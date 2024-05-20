from neo4j import GraphDatabase

from config import config


driver = GraphDatabase.driver(
    config.neo4j_url, 
    auth=(
        config.neo4j_username, 
        config.neo4j_password
    )
)
