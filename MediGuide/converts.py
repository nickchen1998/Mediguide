import os
import pathlib
import tomllib
import chains
import schemas
import utils
from pymongo.collection import Collection
from langchain_openai.embeddings import OpenAIEmbeddings


def calculate_symptom_summary():
    with utils.get_mongo_database() as database:
        collection: Collection = database["symptom"]
        for data in collection.find({"summary": None}):
            symptom = schemas.Symptom(**data)
            # 產生症狀摘要
            symptom_summary = chains.get_symptom_summary_chain(symptom)
            collection.update_one({"_id": symptom.id}, {"$set": {"summary": symptom_summary}})
            print(symptom_summary)


def calculate_symptom_summary_embedding():
    if os.getenv("OPENAI_API_KEY") is None:
        secret_file = pathlib.Path(__file__).parent / ".streamlit" / "secrets.toml"
        with open(secret_file, "rb") as f:
            config = tomllib.load(f)
        os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]

    with utils.get_mongo_database() as database:
        collection: Collection = database["symptom"]
        for data in collection.find({"summary_embedding": None}):
            symptom = schemas.Symptom(**data)
            embedding = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model="text-embedding-3-small"
            ).embed_query(symptom.summary)
            collection.update_one({"_id": symptom.id}, {"$set": {"summary_embedding": embedding}})


if __name__ == '__main__':
    calculate_symptom_summary()
