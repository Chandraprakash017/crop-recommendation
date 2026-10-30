
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

try:
    db = client["crop_recommendation"]

    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "N", "P", "K", "temperature",
                "humidity", "ph", "rainfall", "label"
            ],
            "properties": {
                "N": {"bsonType": ["int", "double", "long", "decimal"]},
                "P": {"bsonType": ["int", "double", "long", "decimal"]},
                "K": {"bsonType": ["int", "double", "long", "decimal"]},
                "temperature": {"bsonType": ["int", "double", "long", "decimal"]},
                "humidity": {"bsonType": ["int", "double", "long", "decimal"]},
                "ph": {"bsonType": ["int", "double", "long", "decimal"]},
                "rainfall": {"bsonType": ["int", "double", "long", "decimal"]},
                "label": {"bsonType": "string"}
            }
        }
    }

    # Apply validation to the existing collection
    db.command({
        "collMod": "crop_samples",
        "validator": validator,
        "validationLevel": "strict",
        "validationAction": "error"
    })

    print("Schema validation enabled!")

finally:
    client.close()
