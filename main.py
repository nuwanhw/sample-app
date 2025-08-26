from fastapi import FastAPI, HTTPException, Request
from pymongo import MongoClient
from bson import ObjectId
import os

# MongoDB Atlas connection (requires MONGO_URI env variable)
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable is required")
client = MongoClient(MONGO_URI)
db = client["testdb"]

app = FastAPI()

def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@app.get("/{entity}")
def get_all(entity: str):
    return [serialize(doc) for doc in db[entity].find()]

@app.get("/{entity}/{item_id}")
def get_by_id(entity: str, item_id: str):
    item = db[entity].find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return serialize(item)

@app.post("/{entity}")
async def save_new(entity: str, request: Request):
    data = await request.json()
    result = db[entity].insert_one(data)
    return serialize(db[entity].find_one({"_id": result.inserted_id}))

@app.put("/{entity}/{item_id}")
async def update(entity: str, item_id: str, request: Request):
    data = await request.json()
    result = db[entity].update_one({"_id": ObjectId(item_id)}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return serialize(db[entity].find_one({"_id": ObjectId(item_id)}))