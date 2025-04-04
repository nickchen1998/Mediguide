import streamlit as st
from langchain_openai import ChatOpenAI
from datetime import date
import time
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import tempfile

openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(page_title="智慧問診機器人", page_icon="🩺")

# 初始化對話紀錄
if 'history' not in st.session_state:
    st.session_state['history'] = []

# 側邊欄：輸入個人資料
with st.sidebar:
    st.header("📝 基本資料填寫")
    name = st.text_input("姓名")
    id_number = st.text_input("身分證字號")
    birthday = st.date_input("出生年月日", value=date(2000, 1, 1))
    blood_type = st.selectbox("血型", ["A", "B", "AB", "O"])

    st.markdown("---")
    audio_bytes = audio_recorder(text="🎤 點我開始錄音")
    if audio_bytes:
        st.sidebar.success("✅ 錄音完成，正在辨識...")

        # 使用 Whisper 模型進行語音辨識
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        with open(tmp_file_path, "rb") as audio_file:
            translation = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="zh",
            )

    st.markdown("---")
    st.caption("※ 本頁面僅作為展示用途，所填資料不會被儲存。")

# 主標題
st.title("智慧問診機器人 🩺")
st.write("🔔 **提醒**：本網站僅為問診輔助原型，請勿作為醫療診斷依據。如有身體不適請洽專業醫師。")


# 顯示問診紀錄
def write_history():
    for message in st.session_state['history']:
        with st.chat_message(message['role']):
            st.write(message['content'])


write_history()

# 輸入並處理提問
if question := st.chat_input("請輸入您的訊息..."):
    # 顯示使用者輸入
    with st.chat_message("user"):
        st.write(question)
    st.session_state['history'].append({
        "role": "user",
        "content": question
    })

    # 檢查基本資料是否齊全
    if not all([name, id_number, birthday, blood_type]):
        system_reply = "請先填寫完整的基本資料後再進行問診。"
    else:
        with st.spinner("思考中..."):
            llm = ChatOpenAI(
                model_name="gpt-4o",
                api_key=st.secrets["OPENAI_API_KEY"]
            )
            system_reply = llm.invoke(
                f"請使用繁體中文回答我的問題，我的問題是：\"{question}\""
            ).content

    # 顯示 AI 回答（逐字效果）
    with st.chat_message("ai"):
        placeholder = st.empty()
        text = ""
        for char in system_reply:
            text += char
            placeholder.markdown(text)
            time.sleep(0.02)  # 控制文字跳出速度（越小越快）

    st.session_state['history'].append({
        "role": "ai",
        "content": system_reply
    })

# 顯示問診摘要
if st.session_state['history']:
    with st.expander("📋 問診摘要"):
        st.subheader("👤 使用者資料")
        st.write(f"**姓名**：{name or '（未填寫）'}")
        st.write(f"**身分證字號**：{id_number or '（未填寫）'}")
        st.write(f"**出生年月日**：{birthday.strftime('%Y-%m-%d')}")
        st.write(f"**血型**：{blood_type}")

        st.subheader("💬 問診對話")
        for msg in st.session_state['history']:
            speaker = "使用者" if msg['role'] == "user" else "機器人"
            st.markdown(f"**{speaker}：** {msg['content']}")
