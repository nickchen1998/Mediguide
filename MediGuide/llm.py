from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from typing import List
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage


def get_llm():
    return ChatOpenAI(model_name="gpt-4o")


def get_refactor_answer(paragraph: str):
    prompt = ChatPromptTemplate.from_template(
        """
你是一個專業的醫生，下面是一篇醫生針對某個患者描述的情況的回應，請幫我使用繁體中文做重點整理，讓患者可以更清楚狀況。
請針對我給予的文章做回覆整理，不要使用文章以外的內容做回覆。
----
文章: {paragraph}
"""
    )
    chain = prompt | get_llm()
    return chain.invoke({"paragraph": paragraph}).content


def get_refactor_question(paragraph: str):
    prompt = ChatPromptTemplate.from_template(
        """
你是一個要去診所進行看診的換診，下面是你的問題，請幫我是用繁體中文做重點整理，讓醫生可以更清楚你的症狀。
過程中請不要針對我的病況給予我任何建議，請幫我整理問題就好，並且不要使用文章以外的內容。
我希望可以把內容縮減在 100 字以內，並且使用簡答的方式整理成一句話，並且不要列點。
請直接給我回覆，不需要給予開頭或結尾。
----
文章: {paragraph}
"""
    )
    chain = prompt | get_llm()
    return chain.invoke({"paragraph": paragraph}).content


def get_content_embedding(content: str) -> list:
    env_settings = EnvSettings()
    embedding = OpenAIEmbeddings(
        openai_api_key=env_settings.OPENAI_API_KEY,
        model="text-embedding-3-small"
    )
    return embedding.embed_query(content)


def get_answer(documents: List[Document], question: str) -> str:
    system_prompt = SystemMessage(content="""
你是一個專業的醫生，下面是一些醫生針對過去類似症狀的回覆，請幫我根據這些回覆來針對患者現在的狀況做說明。
- 請勿使用文章以外的內容做回覆。
- 請使用繁體中文做回覆。
- 如果無法使用文章的資訊進行回答，請直接回覆 “這個問題目前無法回答，請切換別的資料集或請洽管理人員。”
----
        """)
    for document in documents:
        system_prompt.content += f"{document.metadata.get('refactor_answer')}\n"
        system_prompt.content += "----\n"

    llm = ChatOpenAI(
        api_key=EnvSettings().OPENAI_API_KEY,
        model_name="gpt-4o"
    )
    return llm.invoke([system_prompt, HumanMessage(content=question)]).content