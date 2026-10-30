
from pathlib import Path

import joblib
import pandas as pd
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "crop_model.joblib"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "Model not found. Run scripts/train_model.py first."
    )

model = joblib.load(MODEL_PATH)

# Example soil and weather values
values = {
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 25.5,
    "humidity": 80.0,
    "ph": 6.5,
    "rainfall": 200.0
}

features = [
    "N", "P", "K", "temperature",
    "humidity", "ph", "rainfall"
]

input_data = pd.DataFrame([values], columns=features)
prediction = str(model.predict(input_data)[0])

print("Input values:", values)
print("Recommended crop:", prediction)

client = MongoClient(
    "mongodb://localhost:27017/",
    serverSelectionTimeoutMS=3000
)

try:
    client.admin.command("ping")

    db = client["crop_recommendation"]
    result = db["predictions"].insert_one({
        "input": values,
        "predicted_crop": prediction,
        "model": "DecisionTreeClassifier"
    })

    print("Prediction saved to MongoDB.")
    print("Prediction document ID:", result.inserted_id)

finally:
    client.close()
