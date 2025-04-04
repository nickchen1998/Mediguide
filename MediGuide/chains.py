from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


def get_user_info_chain(record_text: str):
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
    chain = prompt | ChatOpenAI(model="gpt-4o", temperature=0) | JsonOutputParser()
    return chain.invoke({"record_text": record_text})
