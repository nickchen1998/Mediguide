from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from utils import get_mongo_vectorstore
from langchain.chains.retrieval_qa.base import RetrievalQA


def get_suggestion_chain(question: str):
    prompt = PromptTemplate.from_template(
        """
        你是一位專業的醫生，請根據下列症狀資訊，彙整出一段簡短的醫學建議，回答過程請符合下列規範：
        - 請使用繁體中文回答。
        - 字數請控制在 300 字以內。
        - 請使用 markdown 格式回答，但不需要標題。
        - 請使用簡單的語言讓患者能夠理解，不要有任何專有名詞或英文縮寫。
        - 請針對患者的症狀進行詳細的描述，並提供可能的診斷和建議。
        - 請避免洩漏參考資料中的患者、醫生的個人資訊。
        - 請優先考慮參考資料中的症狀，並給予建議。
        - 如果參考資料都不適合患者的症狀，請告訴患者，目前沒有相對應的參考資料，並給予你的建議。
        - 如果患者的提問與疾病、症狀無關，你可以依照患者的提問回答。
        
        參考資料：
        {context}
        
        患者提問：
        {question}
        """
    )

    with get_mongo_vectorstore() as vectorstore:
        chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model="gpt-4o", temperature=0),
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )

        return chain.invoke({"query": question})


if __name__ == '__main__':
    from pprint import pprint
    pprint(get_suggestion_chain("覺得噁心該怎麼辦？"))
