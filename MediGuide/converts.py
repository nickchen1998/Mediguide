import os
import pathlib
import tomllib
import schemas
import utils
from tqdm import tqdm
from pymongo.collection import Collection
from langchain_openai.embeddings import OpenAIEmbeddings


def calculate_symptom_summary_embedding(department: str):
    if os.getenv("OPENAI_API_KEY") is None:
        secret_file = pathlib.Path(__file__).parent / ".streamlit" / "secrets.toml"
        with open(secret_file, "rb") as f:
            config = tomllib.load(f)
        os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]

    with utils.get_mongo_database() as database:
        collection: Collection = database["Symptom"]
        for data in tqdm(
                collection.find({"question_embeddings": None, "department": department}),
                desc="Calculating summary embeddings"
        ):
            symptom = schemas.Symptom(**data)
            embedding = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model="text-embedding-3-small"
            ).embed_query(symptom.question.replace(" ", "").replace("\n", ""))
            collection.update_one({"_id": symptom.id}, {"$set": {"question_embeddings": embedding}})


if __name__ == '__main__':
    for tmp in ["肝膽腸胃科", "耳鼻喉科", "皮膚科"]:
        calculate_symptom_summary_embedding(tmp)
