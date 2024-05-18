from langchain.chat_models import ChatOpenAI


# TODO：一个单独的进程
# kimi 支持 openai 的平台
model = ChatOpenAI(
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

