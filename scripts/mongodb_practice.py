
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

try:
    client.admin.command("ping")

    db = client["crop_recommendation"]
    collection = db["crop_samples"]

    # READ: Show total documents
    print("Total crops data:", collection.count_documents({}))

    # READ: Find rice samples
    rice = collection.find_one({"label": "rice"})
    print("Rice sample:", rice)

    # UPDATE: Add a note to one rice sample
    if rice:
        result = collection.update_one(
            {"_id": rice["_id"]},
            {"$set": {"practice_note": "Sample updated"}}
        )
        print("Documents updated:", result.modified_count)

        # Verify update
        updated = collection.find_one({"_id": rice["_id"]})
        print("Updated note:", updated.get("practice_note"))

        # DELETE: Remove the temporary note only
        result = collection.update_one(
            {"_id": rice["_id"]},
            {"$unset": {"practice_note": ""}}
        )
        print("Temporary note removed:", result.modified_count)

finally:
    client.close()
