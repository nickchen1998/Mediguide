import os
import time
import tomllib
import pathlib
import tempfile
import contextlib
import streamlit as st

from uuid import uuid4
from openai import OpenAI

from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch


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


@contextlib.contextmanager
def get_mongo_database() -> Database:
    if os.getenv("MONGODB_URI") is None:
        secret_file = pathlib.Path(__file__).parent.parent / "secrets.toml"
        with open(secret_file, "rb") as f:
            config = tomllib.load(f)
        os.environ["MONGODB_URI"] = config["MONGODB_URI"]

    client = MongoClient(host=os.getenv("MONGODB_URI"))
    try:
        yield Database(client, name="IllnessQA")
    finally:
        client.close()


def insert_illness_datas(datas: list):
    with get_mongo_database() as database:
        vector_store = MongoDBAtlasVectorSearch(
            collection=Collection(database, name="illness"),
            embedding=OpenAIEmbeddings(model="text-embedding-3-small", api_key=st.secrets["OPENAI_API_KEY"]),
            index_name="illness_refactor_question",
            relevance_score_fn="cosine",
        )

        documents = []
        for data in datas:
            documents.append(Document(
                page_content=data.pop("refactor_question"),
                metadata=data
            ))

        uuids = [str(uuid4()) for _ in range(len(documents))]
        vector_store.add_documents(documents, uuids)
