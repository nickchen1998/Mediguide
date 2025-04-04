import streamlit as st
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from mongo import get_mongo_database
from pymongo.collection import Collection
from langchain_openai import OpenAIEmbeddings
from llm import get_answer
from export import export_history_to_json
from langchain_openai import ChatOpenAI


def write_history():
    for message in st.session_state['history']:
        with st.chat_message(message['role']):
            st.write(message['content'])


datasets = {
    "排便問題": {
        "dep": "肝膽腸胃科",
        "url": "https://sp1.hso.mohw.gov.tw/doctor/Often_question"
               "/type_detail.php?q_type=%B1%C6%ABK%B0%DD%C3D&UrlClass=%A8x%C1x%B8z%ADG%AC%EC"
    },
    "經痛": {
        "dep": "婦產科",
        "url": "https://sp1.hso.mohw.gov.tw/doctor/Often_question"
               "/type_detail.php?UrlClass=%B0%FC%B2%A3%AC%EC&q_like=0&q_type=%B8g%B5h"
    },
    "藥水": {
        "dep": "眼科",
        "url": "https://sp1.hso.mohw.gov.tw/doctor/Often_question"
               "/type_detail.php?UrlClass=%B2%B4%AC%EC&q_like=0&q_type=%C3%C4%A4%F4"
    }
}

# 初始化對話紀錄及選定資料集
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'selected_dataset' not in st.session_state:
    st.session_state['selected_dataset'] = "排便問題"

with st.sidebar:
    st.title("選擇資料集")
    dataset_option = st.selectbox(
        "請選擇在問答時要使用的資料集...",
        [key for key in datasets.keys()]
    )

    st.title("對話紀錄相關功能")
    if st.button("清空對話紀錄"):
        st.session_state['history'] = []

    if st.download_button(
            "下載對話紀錄",
            export_history_to_json(st.session_state['history']),
            "dialogue.json",
            mime="application/json"
    ):
        st.session_state['history'] = []  # 下載後清空對話紀錄

# 當資料集切換時，刪除對話紀錄
if dataset_option != st.session_state['selected_dataset']:
    st.session_state['selected_dataset'] = dataset_option
    st.session_state['history'] = []

st.title("問答機器人")
st.write("本網站並非專業醫療諮詢網站，僅用於學習系統開發，請勿依賴本網站的資訊作為醫療建議。")
st.write(f"目前選擇的資料集為 ”{dataset_option}“，資料來源可以參考 [這個網址]({datasets[dataset_option]['url']})。")

question = st.chat_input("請輸入您的訊息...")

if question:
    st.session_state['history'].append({
        "role": "user",
        "content": question
    })

    with get_mongo_database() as database:
        vector_store = MongoDBAtlasVectorSearch(
            collection=Collection(database, name="illness"),
            embedding=OpenAIEmbeddings(model="text-embedding-3-small", api_key=st.secrets["OPENAI_API_KEY"]),
            index_name="illness_refactor_question",
            relevance_score_fn="cosine",
        )
        documents = vector_store.similarity_search(
            query=question,
            k=3,
            pre_filter={"category": {"$eq": dataset_option}}
        )
        answer = get_answer(documents, question)
    answer = ChatOpenAI(
        model_name="gpt-4o",
        api_key=st.secrets["OPENAI_API_KEY"]
    ).invoke(f"請使用繁體中文回答我的問題，我的問題是：\"{question}\"").content

    st.session_state['history'].append({
        "role": "ai",
        "content": answer,
        # "references": [doc.metadata.get("refactor_answer") for doc in documents]
    })
    write_history()
