import os
import time
import tempfile
import streamlit as st
from openai import OpenAI


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


def get_record_text_by_whisper(audio_bytes: bytes):
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        api_key = st.secrets["OPENAI_API_KEY"]
    openai_client = OpenAI(api_key=api_key)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_file_path = tmp_file.name
    with open(tmp_file_path, "rb") as audio_file:
        translation = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="zh",
        )

    return translation.text
