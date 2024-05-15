from tqdm import tqdm
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import WikipediaLoader

from db.neo4j import graph
from service.base import extract_and_store_graph

raw_documents = WikipediaLoader(query="Walt Disney").load()
text_splitter = TokenTextSplitter(chunk_size=2048, chunk_overlap=24)
documents = text_splitter.split_documents(raw_documents[:3])

allowed_nodes = [
    "Person", 
    "Company", 
    "Location", 
    "Event", 
    "Movie", 
    "Service", 
    "Award"
]

for i, d in tqdm(enumerate(documents), total=len(documents)):
    extract_and_store_graph(d, allowed_nodes)

graph.refresh_schema()
cypher_chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=ChatOpenAI(temperature=0, model="gpt-4"),
    qa_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
    validate_cypher=True,
    verbose=True
)

cypher_chain.invoke({"query": "When was Walter Elias Disney born?"})
