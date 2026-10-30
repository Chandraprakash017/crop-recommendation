
from pathlib import Path

import joblib
import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

client = MongoClient("mongodb://localhost:27017/")

try:
    db = client["crop_recommendation"]
    collection = db["crop_samples"]

    # Read training data from MongoDB
    records = list(collection.find({}, {"_id": 0}))
    df = pd.DataFrame(records)

    if len(df) < 1000:
        raise ValueError("Dataset must contain at least 1000 rows.")

    features = [
        "N", "P", "K", "temperature",
        "humidity", "ph", "rainfall"
    ]
    target = "label"

    X = df[features]
    y = df[target]

    # 70% training data, 30% testing data
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y
    )

    # Train Decision Tree
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Evaluate on unseen test data
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("Total rows:", len(df))
    print("Training rows:", len(X_train))
    print("Testing rows:", len(X_test))
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification report:")
    print(classification_report(y_test, predictions))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, predictions))

    # Save the trained model
    model_path = MODEL_DIR / "crop_model.joblib"
    joblib.dump(model, model_path)
    print("\nModel saved at:", model_path)

    # Save evaluation summary to MongoDB
    db["model_runs"].insert_one({
        "model": "DecisionTreeClassifier",
        "dataset_rows": int(len(df)),
        "training_rows": int(len(X_train)),
        "testing_rows": int(len(X_test)),
        "accuracy": float(accuracy),
        "features": features,
        "target": target,
        "test_size": 0.30,
        "random_state": 42
    })

finally:
    client.close()
