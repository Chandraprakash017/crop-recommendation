
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

try:
    db = client["crop_recommendation"]
    collection = db["crop_samples"]

    pipeline = [
        {
            "$group": {
                "_id": "$label",
                "sample_count": {"$sum": 1},
                "average_temperature": {"$avg": "$temperature"},
                "average_rainfall": {"$avg": "$rainfall"}
            }
        },
        {"$sort": {"sample_count": -1, "_id": 1}}
    ]

    results = collection.aggregate(pipeline)

    print("Crop-wise statistics:")
    for item in results:
        print(
            item["_id"],
            "| Samples:", item["sample_count"],
            "| Avg temperature:", round(item["average_temperature"], 2),
            "| Avg rainfall:", round(item["average_rainfall"], 2)
        )

finally:
    client.close()
