from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from models import StoreModel
from schemas import PlainStoreSchema, StoreSchema
from db import db

blp = Blueprint("stores", __name__, description=("Stores requests:"))


@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        try:
            store = StoreModel.query.get_or_404(store_id)
            return store
        except SQLAlchemyError:
            abort(500, message="Not able to retrieve data from our database")

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        try:
            db.session.delete(store)
            db.session.commit()
            return {"message": "Store deleted succesfully"}
        except SQLAlchemyError:
            abort(500, message="Not able to delete store from our database")


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, PlainStoreSchema(many=True))
    def get(self):
        try:
            stores = StoreModel.query.all()
            return stores
        except SQLAlchemyError:
            abort(500, message="Not able to retrieve data from our database")

    # Middleware validacao/response
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, validated_store_data):
        store = StoreModel(**validated_store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A Store with this name already exists")
        except SQLAlchemyError:
            abort(500, message="Not able to create the store in our database")

        return store
