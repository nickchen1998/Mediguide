import os
import utils
import chains
import streamlit as st

from datetime import date
from audio_recorder_streamlit import audio_recorder

if os.environ.get("OPENAI_API_KEY") is None:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
if 'history' not in st.session_state:
    st.session_state['history'] = []

st.set_page_config(page_title="智慧問診機器人", page_icon="🩺")

with st.sidebar:
    st.header("📝 基本資料填寫")
    name = st.text_input("姓名", value=st.session_state.get("name", ""))
    id_number = st.text_input("身分證字號", value=st.session_state.get("id_number", ""))
    birthday = st.date_input("出生年月日", value=st.session_state.get("birthday", "today"))
    blood_type = st.selectbox(
        "血型", ["", "A", "B", "AB", "O"],
        index=["", "A", "B", "AB", "O"].index(st.session_state.get("blood_type", ""))
    )

    if audio_bytes := audio_recorder(text="使用聲音輔助輸入", icon_size="15px"):
        if not st.session_state.get("recognized", False) and len(audio_bytes) / (1024 * 1024) > 0.1:
            st.sidebar.success("✅ 錄音完成，正在辨識...")
            try:
                record_text = utils.get_record_text_by_whisper(audio_bytes)
                user_info = chains.get_user_info_chain(record_text)

                st.session_state["name"] = user_info.get("name", "")
                st.session_state["id_number"] = user_info.get("id_number", "")
                if user_info.get("birthday"):
                    st.session_state["birthday"] = date.fromisoformat(user_info["birthday"])
                if user_info.get("blood_type"):
                    st.session_state["blood_type"] = user_info.get("blood_type")

                st.session_state["recognized"] = True
                st.sidebar.success("✅ 辨識完成，請查閱上方基本資料是否正確！")
                st.rerun()
            except Exception as e:
                print(e)
                st.sidebar.error("❌ 辨識失敗，請稍後再試。")
                st.session_state["recognized"] = False
    else:
        st.session_state["recognized"] = False

    st.markdown("---")
    st.caption("※ 本頁面僅作為展示用途，所填資料不會被儲存。")

# 問診區塊
st.title("智慧問診機器人 🩺")
st.markdown("🔔 **提醒**：本網站僅為問診輔助原型，請勿作為醫療診斷依據，如有身體不適請洽專業醫師。")
utils.write_history()

# 問診輸入區
if question := st.chat_input("請輸入您的訊息..."):
    utils.set_chat_message("user", question)

    if not all([name, id_number, birthday, blood_type]):
        utils.set_chat_message("ai", "請先填寫基本資料，再進行問答！")
    else:
        symptoms = utils.get_symptom_by_embeddings(question)
        system_reply = chains.get_suggest_with_symptom_chain(
            question=question, symptoms=symptoms
        )
        utils.set_chat_message("ai", system_reply, [{
            "_id": str(symptom.id),
            "department": symptom.department,
            "symptom": symptom.symptom,
            "summary": symptom.summary,
        } for symptom in symptoms])

# 顯示問診摘要
if st.session_state['history'] and not st.session_state['history'][-1]['content'] == "請先填寫基本資料，再進行問答！":
    with st.expander("📋 問診結果"):
        st.subheader("👤 使用者資料")
        st.write(f"**姓名**：{name or '（未填寫）'}")
        st.write(f"**身分證字號**：{id_number or '（未填寫）'}")
        st.write(f"**出生年月日**：{birthday.strftime('%Y-%m-%d')}")
        st.write(f"**血型**：{blood_type}")

        st.subheader("💬 問診對話")
        for msg in st.session_state['history'][-2:]:
            speaker = "使用者" if msg['role'] == "user" else "機器人"
            st.markdown(f"**{speaker}：** {msg['content']}")

        st.subheader("📑 參考資料")
        for reference in st.session_state['history'][-1]['references']:
            st.markdown(f"- **_id**：{reference['_id']}")
            st.markdown(f"- **科別**：{reference['department']}")
            st.markdown(f"- **症狀分類**：{reference['symptom']}")
            st.markdown(f"- **摘要**：{reference['summary']}")
            st.markdown("---")
