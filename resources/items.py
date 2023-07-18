from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity

from schemas.schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel
from db import db

blp = Blueprint("items", __name__, description="Items requests: ")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        try:
            item = ItemModel.query.get_or_404(item_id)
            return item
        except SQLAlchemyError:
            abort(500, message="Not able to retrieve data from our database")

    @jwt_required()  # token middleware
    @blp.arguments(ItemUpdateSchema)  # Middleware
    @blp.response(200, ItemSchema)
    def put(self, validated_item_data, item_id):
        item = ItemModel.query.get(item_id)

        if not item:
            abort(400, message="The provided id does not match any item")

        for key, value in validated_item_data.items():
            setattr(item, key, value)

        try:
            db.session.add(item)
            db.session.commit()
            return item
        except SQLAlchemyError:
            abort(500, message="Not able to update data in our database")

    @jwt_required()
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        try:
            db.session.delete(item)
            db.session.commit()
            return {"message": "Item deleted"}, 200
        except SQLAlchemyError:
            abort(500, message="Not able to delete item from our database")


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        try:
            items = ItemModel.query.all()
            return items
        except SQLAlchemyError:
            abort(500, message="Not able to retrieve data from our database")

    @jwt_required()  # verifica token
    # Middleware -> Valida o request e passa um argument pra funcao seguinte
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, validated_item_data):
        jwt_identity = get_jwt_identity()
        # item_data = request.get_json() -> substituido pelo middleware @blp.arguments
        item = ItemModel(**validated_item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, "Not able to insert the item in our database")

        return item
