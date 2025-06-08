import os
import time
import tomllib
import pathlib
import contextlib
import streamlit as st

from typing import List
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


def set_chat_message(role, content, references=None):
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
        "content": content,
        "references": references
    })


@contextlib.contextmanager
def get_mongo_vectorstore() -> MongoDBAtlasVectorSearch:
    if os.getenv("MONGODB_URI") is None:
        secret_file = pathlib.Path(__file__).parent / ".streamlit" / "secrets.toml"
        with open(secret_file, "rb") as f:
            config = tomllib.load(f)
        os.environ["MONGODB_URI"] = config["MONGODB_URI"]

    if os.getenv("OPENAI_API_KEY") is None:
        secret_file = pathlib.Path(__file__).parent / ".streamlit" / "secrets.toml"
        with open(secret_file, "rb") as f:
            config = tomllib.load(f)
        os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]

    client = MongoClient(host=os.getenv("MONGODB_URI"))
    try:
        database = Database(client, name="MediGuide")
        vectorstore = MongoDBAtlasVectorSearch(
            collection=Collection(database, name="Symptom"),
            embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
            index_name="default",
            embedding_key="question_embeddings",
            text_key="question"
        )

        yield vectorstore
    finally:
        client.close()


def insert_symptom_subject_datas(datas: List[dict]):
    with get_mongo_vectorstore() as vectorstore:
        documents = []
        for data in datas:
            if vectorstore.collection.find_one({"subject_id": data["subject_id"]}):
                continue

            documents.append(Document(
                page_content=data.pop("question"),
                metadata=data
            ))

        vectorstore.add_documents(documents, batch_size=100)
