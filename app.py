import uuid
from flask import Flask, request
from db import items, stores

app = Flask(__name__)


@app.get("/store")
def get_stores():
    return {"stores": list(stores.values())}


@app.post("/store")
def create_store():
    store_data = request.get_json()
    store_id = uuid.uuid4().hex
    new_store = {**store_data, "id": store_id}
    stores[store_id] = new_store
    return new_store, 201


# Params
@app.post("/item")
def create_item():
    item_data = request.get_json()

    if item_data["store_id"] in stores:
        item_id = uuid.uuid4().hex
        items[item_id] = {**item_data, "id": item_id}
        return items[item_id], 201

    return {"message": "Store not found"}, 404


@app.get("/item")
def get_items():
    return {"items": list(items.values())}


@app.get("/store/<string:store_id>")
def get_store_by_id(store_id):
    try:
        return stores[store_id]
    except KeyError:
        return {"message": "Store not found"}, 404


@app.get("/item/<string:item_id>")
def get_store_items(item_id):
    try:
        return items[item_id]
    except KeyError:
        return {"message": "Item not found"}, 404
