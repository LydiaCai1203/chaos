"""
https://python.langchain.com/v0.1/docs/use_cases/graph/constructing/
"""
from tqdm import tqdm
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain.text_splitter import TokenTextSplitter
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from service.base import extract_and_store_graph
from db.neo4j import driver


raw = (
    "于连，一个出身低微的木匠之子，凭借才华和野心，渴望改变自己的命运。"
    "他首先成为市长家的家教，并与市长的妻子德雷娜夫人发生了不伦之恋。"
    "这段关系几乎被揭露时，于连忙转至省城的神学院，之后在侯爵府中得到职位，开始了他的上层社会生活。"
    "在侯爵府，于连以聪明才智和文化素养赢得了侯爵的信任和女儿马蒂尔德的注意。"
    "马蒂尔德对于连产生了复杂的感情，而于连则试图利用这段关系攀升社会阶梯。"
    "两人的关系经历了从热情到疏远再到激情重燃的波折。"
    "于连的野心和行为最终引起了侯爵的怀疑，尤其是当侯爵得知于连可能涉及勾引其他贵族女性时。"
    "同时，于连因过去与德雷娜夫人的关系而受到指责。"
    "在一系列复杂的情感和社交压力下，于连向德雷娜夫人开枪，虽未致命，但此举导致他被捕并判处死刑。"
    "在监狱中，于连反思了自己的一生，而马蒂尔德和德雷娜夫人都试图为他辩护和争取宽恕。"
    "然而，于连拒绝了所有上诉的机会，坚持认为自己的行为是罪有应得。"
    "最终，于连在刑场上坦然面对死刑，而马蒂尔德和德雷娜夫人则因他的死而悲痛欲绝。"
    "德雷娜夫人在于连死后不久离世，马蒂尔德则孤独地继续生活。"
    "《红与黑》通过于连的故事，展示了个人野心与社会阶级的冲突，探讨了真诚与虚伪、爱情与权力之间的复杂关系。"
)
text_splitter = TokenTextSplitter(chunk_size=2048, chunk_overlap=24)
documents = text_splitter.create_documents([raw])

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
llm_transformer_filtered = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["人", "国家", "地点"],
    allowed_relationships=[],
)
graph_documents_filtered = llm_transformer_filtered.convert_to_graph_documents(documents)

print(f"Nodes:{graph_documents_filtered[0].nodes}")
print(f"Relationships:{graph_documents_filtered[0].relationships}")


# graph.refresh_schema()
# cypher_chain = GraphCypherQAChain.from_llm(
#     graph=graph,
#     cypher_llm=llm,
#     qa_llm=llm,
#     validate_cypher=True,
#     verbose=True
# )

# cypher_chain.invoke({"query": "于连的结局是什么?"})
