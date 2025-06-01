from typing import List
from schemas import Symptom
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch


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


def get_symptom_summary_chain(symptom: Symptom):
    prompt = PromptTemplate.from_template(
        """
        你是一位專業的醫生，請根據下列症狀資訊，彙整出一段簡短的醫學摘要，回答過程請符合下列規範：
        - 請使用繁體中文回答。
        - 請使用 markdown 格式回答。
        - 請使用簡單的語言讓患者能夠理解，不要有任何專有名詞或英文縮寫。
        - 請針對患者的症狀進行詳細的描述，並提供可能的診斷和建議。
        - 文章長度請落在大約 300 字左右。
        - 請不要將患者的名稱、醫生的名稱或醫院名稱寫入摘要中，避免個資疑慮。
        
        ----
        範例：
        - 就診科別：耳鼻喉科
        - 症狀分類：噁心
        - 患者主訴標題：噁心、頭暈
        - 患者主訴內容：前天睡前突然噁心，但將上半身墊高後症狀就舒緩得入睡。昨天起床噁心的症狀持續，吃不下任何食物，只喝了開水和一口能量飲料(應德)當早餐，也服用了一粒固胃保寧，但沒什麼效果。下午三點後就陸續可以進食，晚上用了比平常久的吃飯時間吃到正常分量。今天起床後症狀消失，所以照原定計畫和朋友聚餐，食量也無影響。但是晚上在家吃晚餐的時候突然又覺得噁心頭暈，所以沒有吃完。平常有脹氣和便秘的問題，也經常熬夜，頻繁喝茶，但已經正常排便兩天，平常喝茶也沒有醉茶的反應。請問有什麼辦法可以舒緩噁心的症狀，或需要看醫生檢查嗎?另外我這兩天常在戶外活動，有可能是中暑嗎?
        - 醫生回覆內容：您好:食物跟飲料，要避開刺激性，油炸類，不要吃太快吃太飽。如果懷疑中暑，可以多補充水份，避免過度日晒。另外，逆流性食道炎，胃炎，也都可能有類似症狀。可以就診胃腸科，查明原因。彰化醫院關心您的健康 蔡安順醫師
        
        產生出的摘要：
        患者這兩天反覆出現噁心和頭暈，症狀有時在進食後緩解，但也會突然再度發作。平時有脹氣、便秘、熬夜及常喝茶的習慣，近期也有在戶外活動，因此懷疑是否為中暑引起。
        醫師建議如下：
        飲食調整：避免油炸、辛辣、刺激性食物，進食時要慢，不宜過量。
        補充水分：若懷疑中暑，應多喝水，並避免長時間日曬。
        檢查腸胃功能：症狀也可能與胃炎或胃食道逆流有關，建議就診腸胃科進一步確認。
        建議不要忽視反覆出現的不適症狀，儘早尋求專業協助以確保健康。
        ----
        本次案例：
        - 就診科別：{department}
        - 症狀分類：{symptom}
        - 患者主訴標題：{subject}
        - 患者主訴內容：{question}
        - 醫生回覆內容：{answer}
        
        產生出的摘要：
        <請協助我產生摘要>
        """
    )
    chain = prompt | ChatOpenAI(model="gpt-4o", temperature=0)
    return chain.invoke({
        "department": symptom.department,
        "symptom": symptom.symptom,
        "subject": symptom.subject,
        "question": symptom.question,
        "answer": symptom.answer
    }).content


def get_suggest_with_symptom_chain(symptoms: List[Symptom], question: str):
    prompt = PromptTemplate.from_template(
        """
        你是一位專業的醫生，請根據下列症狀資訊，彙整出一段簡短的醫學建議，回答過程請符合下列規範：
        - 請使用繁體中文回答。
        - 字數請控制在 300 字以內。
        - 請使用 markdown 格式回答，蛋不需要標題。
        - 請使用簡單的語言讓患者能夠理解，不要有任何專有名詞或英文縮寫。
        - 請針對患者的症狀進行詳細的描述，並提供可能的診斷和建議。
        - 請避免洩漏參考資料中的患者、醫生的個人資訊。
        - 請優先考慮參考資料中的症狀，並給予建議。
        - 如果參考資料都不適合患者的症狀，請告訴患者，目前沒有相對應的參考資料，並給予你的建議。
        - 如果患者的提問與疾病、症狀無關，你可以依照患者的提問回答。
        
        參考資料：
        {references}
        
        患者提問：
        {question}
        """
    )
    chain = prompt | ChatOpenAI(model="gpt-4o", temperature=0)
    return chain.invoke({
        "references": '----------'.join([tmp.answer for tmp in symptoms]),
        "question": question
    }).content
