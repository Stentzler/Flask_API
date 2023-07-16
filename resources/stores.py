from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from models import StoreModel
from schemas.schemas import PlainStoreSchema, StoreSchema
from db import db

blp = Blueprint("stores", __name__, description=("Stores requests:"))


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted succesfully"}


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, PlainStoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    # Middleware validacao
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
            abort(500, message="Not able to create the store")

        return store
