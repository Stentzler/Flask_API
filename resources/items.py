from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas.schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel, StoreModel
from db import db

blp = Blueprint("items", __name__, description="Items requests: ")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @blp.arguments(ItemUpdateSchema)  # Middleware
    @blp.response(200, ItemSchema)
    def put(self, validated_item_data, item_id):
        item = ItemModel.query.get(item_id)

        if not item:
            abort(400, message="The provided id does not match any item")

        if "store_id" in validated_item_data:
            store = StoreModel.query.get(validated_item_data["store_id"])
            if not store:
                abort(400, message="The provided id does not match any Store")

        for key, value in validated_item_data.items():
            setattr(item, key, value)

        db.session.add(item)
        db.session.commit()
        return item

    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()

        return {"message": "Item deleted"}, 200


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    # Middleware -> Valida o request e passa um argument pra funcao seguinte
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, validated_item_data):
        # item_data = request.get_json() -> substituido pelo middleware @blp.arguments
        item = ItemModel(**validated_item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, "Not able to insert the item")

        return item
