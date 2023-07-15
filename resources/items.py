import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import items, stores

blp = Blueprint("items", __name__, description="Items requests: ")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    def get(self, item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(404, message="Item not found")

    def put(self, item_id):
        update_data = request.get_json()

        # Validating the JSON payload
        if "price" not in update_data or "name" not in update_data:
            abort(
                400,
                message='Ensure to provide the following properties in your JSON payload: "name", "price"',
            )
        try:
            ##-- Shortcut para MERGE de dicts items[item_id] = {**items[item_id], **update_data}
            items[item_id] |= update_data
            return items[item_id]
        except:
            abort(
                404,
                message="No item found for the provided id",
            )

    def delete(self, item_id):
        try:
            del items[item_id]
            return {"message": "item deleted"}
        except:
            abort(404, message="Item not found")


@blp.route("/item")
class ItemList(MethodView):
    def get(self):
        return {"items": list(items.values())}

    def post(self):
        item_data = request.get_json()

        # Validating the JSON payload
        if (
            "price" not in item_data
            or "store_id" not in item_data
            or "name" not in item_data
        ):
            abort(
                400,
                'Ensure to provide the following properties in your JSON payload: "name", "price" and "store_id"',
            )
        # Validating duplicated item name
        for item in items.values():
            if (
                item_data["name"] == item["name"]
                and item_data["store_id"] == item["store_id"]
            ):
                abort(
                    400, message=f"{item['name']} is already registered in this store"
                )
        # Adding to DB
        if item_data["store_id"] in stores:
            item_id = uuid.uuid4().hex
            items[item_id] = {**item_data, "id": item_id}
            return items[item_id], 201

        abort(404, message="Store not found")
