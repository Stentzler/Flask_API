import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import items, stores
from schemas.schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("items", __name__, description="Items requests: ")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(404, message="Item not found")

    @blp.arguments(ItemUpdateSchema)  # Middleware
    @blp.response(200, ItemSchema)
    def put(self, validated_item_data, item_id):
        try:
            ##-- Shortcut para MERGE de dicts items[item_id] = {**items[item_id], **validated_item_data}
            items[item_id] |= validated_item_data
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
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return items.values()

    # Middleware -> Valida o request e passa um argument pra funcao seguinte
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, validated_item_data):
        # item_data = request.get_json() -> substituido pelo middleware @blp.arguments

        # Validating duplicated item name
        for item in items.values():
            if (
                validated_item_data["name"] == item["name"]
                and validated_item_data["store_id"] == item["store_id"]
            ):
                abort(
                    400, message=f"{item['name']} is already registered in this store"
                )

        # Adding to DB
        if validated_item_data["store_id"] in stores:
            item_id = uuid.uuid4().hex
            items[item_id] = {**validated_item_data, "id": item_id}
            return items[item_id]

        abort(404, message="Store not found")
