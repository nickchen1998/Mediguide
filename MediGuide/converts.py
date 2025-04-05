import os
import pathlib
import tomllib
import chains
import schemas
import utils
from tqdm import tqdm
from pymongo.collection import Collection
from langchain_openai.embeddings import OpenAIEmbeddings


def calculate_symptom_summary(department: str):
    if os.getenv("OPENAI_API_KEY") is None:
        secret_file = pathlib.Path(__file__).parent / ".streamlit" / "secrets.toml"
        with open(secret_file, "rb") as f:
            config = tomllib.load(f)
        os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]

    with utils.get_mongo_database() as database:
        collection: Collection = database["Symptom"]
        for data in tqdm(collection.find({"summary": None, "department": department}), desc="Calculating summary"):
            symptom = schemas.Symptom(**data)
            symptom_summary = chains.get_symptom_summary_chain(symptom)
            collection.update_one({"_id": symptom.id}, {"$set": {"summary": symptom_summary}})


def calculate_symptom_summary_embedding(department: str):
    if os.getenv("OPENAI_API_KEY") is None:
        secret_file = pathlib.Path(__file__).parent / ".streamlit" / "secrets.toml"
        with open(secret_file, "rb") as f:
            config = tomllib.load(f)
        os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]

    with utils.get_mongo_database() as database:
        collection: Collection = database["Symptom"]
        for data in tqdm(
                collection.find({"summary_embeddings": None, "summary": {"$ne": None}, "department": department}),
                desc="Calculating summary embeddings"
        ):
            symptom = schemas.Symptom(**data)
            embedding = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model="text-embedding-3-small"
            ).embed_query(symptom.summary)
            collection.update_one({"_id": symptom.id}, {"$set": {"summary_embeddings": embedding}})


if __name__ == '__main__':
    for tmp in ["肝膽腸胃科", "耳鼻喉科", "皮膚科"]:
        calculate_symptom_summary(tmp)
        calculate_symptom_summary_embedding(tmp)
