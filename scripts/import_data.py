
from pathlib import Path

import pandas as pd
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "Crop_recommendation.csv"

df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.strip()

required_columns = [
    "N", "P", "K", "temperature",
    "humidity", "ph", "rainfall", "label"
]

if not set(required_columns).issubset(df.columns):
    raise ValueError("Dataset columns do not match!")

df = df[required_columns].dropna()

# Convert dataset rows into MongoDB documents
records = df.to_dict(orient="records")

client = MongoClient(
    "mongodb://localhost:27017/",
    serverSelectionTimeoutMS=3000
)

try:
    client.admin.command("ping")

    db = client["crop_recommendation"]
    collection = db["crop_samples"]

    # Avoid duplicate imports when running the script again
    collection.delete_many({})

    result = collection.insert_many(records)

    print("Import successful!")
    print("Rows imported:", len(result.inserted_ids))
    print("MongoDB document count:", collection.count_documents({}))

finally:
    client.close()
