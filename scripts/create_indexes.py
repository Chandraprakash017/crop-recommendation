
from pymongo import MongoClient, ASCENDING

client = MongoClient("mongodb://localhost:27017/")

try:
    client.admin.command("ping")

    db = client["crop_recommendation"]

    samples = db["crop_samples"]
    predictions = db["predictions"]

    # Index for filtering crops by label
    samples.create_index([("label", ASCENDING)])

    # Index for searching predictions by predicted crop
    predictions.create_index([("predicted_crop", ASCENDING)])

    print("Indexes created successfully!")

    print("\nCrop sample indexes:")
    print(samples.index_information())

    print("\nPrediction indexes:")
    print(predictions.index_information())

finally:
    client.close()
