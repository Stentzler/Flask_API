import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import stores
from schemas.schemas import StoreSchema

blp = Blueprint("stores", __name__, description=("Stores requests:"))


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(404, message="Store not found")

    def delete(self, store_id):
        try:
            del stores[store_id]
            return {"message": "Store deleted successfully"}
        except:
            abort(404, message="Store not found for the provided id")


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return stores.values()

    # Middleware validacao
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, validated_store_data):
        # Validating if store already exists
        for store in stores.values():
            if validated_store_data["name"] == store["name"]:
                abort(400, message=f"Store {store['name']} already registered")

        # Creating new store
        store_id = uuid.uuid4().hex
        stores[store_id] = {**validated_store_data, "id": store_id}
        return stores[store_id]
