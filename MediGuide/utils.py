import time
import streamlit as st


def write_history():
    for message in st.session_state['history']:
        with st.chat_message(message['role']):
            st.write(message['content'])


def set_chat_message(role, content):
    if role == "ai":
        with st.chat_message("ai"):
            placeholder = st.empty()
            text = ""
            for char in content:
                text += char
                placeholder.markdown(text)
                time.sleep(0.02)  # 控制文字跳出速度（越小越快）
    else:
        with st.chat_message(role):
            st.write(content)

    st.session_state['history'].append({
        "role": role,
        "content": content
    })
