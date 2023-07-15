import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import stores

blp = Blueprint("stores", __name__, description=("Stores requests:"))


@blp.route("/store/<string:store_id>")
class Store(MethodView):
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
    def get(self):
        return {"stores": list(stores.values())}

    def post(self):
        store_data = request.get_json()

        # Validating the JSON payload
        if "name" not in store_data:
            abort(
                400,
                'Ensure to provide the following properties in your JSON payload: "name"',
            )

        # Validating if store already exists
        for store in stores.values():
            if store_data["name"] == store["name"]:
                abort(400, message=f"Store {store['name']} already registered")

        # Creating new store
        store_id = uuid.uuid4().hex
        new_store = {**store_data, "id": store_id}
        stores[store_id] = new_store
        return new_store, 201
