from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils import get_mongo_vectorstore, get_record_text_by_whisper
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.runnables import RunnableLambda


def get_user_info_by_record_chain(audio_bytes: bytes):
    prompt = PromptTemplate.from_template(
        """
        你是一位表單資料解析助手，請根據下列輸入句子，擷取使用者的基本資料並以 JSON 格式輸出：
        - 姓名：name（string）
        - 身分證字號：id_number（string）
        - 出生年月日：birthday（格式為 YYYY-MM-DD）
        - 血型：blood_type（僅為 A、B、AB 或 O）
    
        如果使用者未說明某一欄位，請填入 null。
    
        請分析這句話：
        「{record_text}」
    
        並輸出如下格式：
        {{
            "name": ...,
            "id_number": ...,
            "birthday": ...,
            "blood_type": ...
        }}
        """
    )
    chain = (
            RunnableLambda(get_record_text_by_whisper) |
            prompt |
            ChatOpenAI(model="gpt-4o", temperature=0) |
            JsonOutputParser()
    )
    return chain.invoke(audio_bytes)


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
