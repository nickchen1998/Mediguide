import utils
import chains
import streamlit as st
from datetime import date

if 'history' not in st.session_state:
    st.session_state['history'] = []

st.set_page_config(page_title="智慧問診機器人", page_icon="🩺")

with st.sidebar:
    st.header("📝 基本資料填寫")
    name = st.text_input("姓名", value=st.session_state.get("name", ""))
    id_number = st.text_input("身分證字號", value=st.session_state.get("id_number", ""))
    birthday = st.date_input(
        "出生年月日", value=st.session_state.get("birthday", "today"),
        min_value="1900-01-01", max_value=date.today()
    )
    blood_type = st.selectbox(
        "血型", ["", "A", "B", "AB", "O"],
        index=["", "A", "B", "AB", "O"].index(st.session_state.get("blood_type", ""))
    )

    st.markdown("---")
    st.caption("※ 本頁面僅作為展示用途，資料不會被儲存。")
    st.caption("※ 本站台資料來源為 “衛生福利部 - 台灣 e 院”，https://sp1.hso.mohw.gov.tw/doctor/ 。")
    st.caption("※ 目前支援問診的科別為 肝膽腸胃科、皮膚科、耳鼻喉科，未來會視情況進行擴充。")

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
        try:
            suggestion = chains.get_suggestion_chain(question=question)
            utils.set_chat_message(
                "ai",
                suggestion.get("result"),
                [{"_id": document.metadata.get("_id"),
                  "department": document.metadata.get("department"),
                  "symptom": document.metadata.get("symptom"),
                  "answer": document.metadata.get("answer"),
                  "question": document.page_content,
                  } for document in suggestion.get("source_documents", [])])
        except Exception as e:
            print(e)
            utils.set_chat_message("ai", "很抱歉，目前無法回答您的問題，請稍後再試或通知管理人員。")

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

        if st.session_state['history'][-1].get('references'):
            st.subheader("📑 參考資料")
            for reference in st.session_state['history'][-1]['references']:
                st.markdown(f"- **_id**：{reference['_id']}")
                st.markdown(f"- **症狀分類**：{reference['department']} / {reference['symptom']}")
                st.markdown(f"- **患者主訴**：")
                st.markdown(f"{reference['question']}")
                st.markdown(f"- **醫師回覆**：")
                st.markdown(f"{reference['answer'].replace('回覆', '')}")
                st.write("---")
