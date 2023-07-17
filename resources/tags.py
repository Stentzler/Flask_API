from sqlalchemy.exc import SQLAlchemyError
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from models import TagModel, StoreModel, ItemModel, ItemsTagsModel
from schemas import TagSchema, ItemsTagsSchema, PlainTagSchema
from db import db

blp = Blueprint("tags", __name__, description=("Tags requests:"))


@blp.route("/store/<string:store_id>/tag")
class TagsFromStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get(store_id)

        if not store:
            abort(400, message="No store found for the provided Id")

        tags_store = TagModel.query.filter(TagModel.store_id == store_id).all()
        return tags_store
        # return store.tags.all()  #Mesmo resultado!

    @blp.arguments(PlainTagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        if TagModel.query.filter(
            TagModel.store_id == store_id, TagModel.name == tag_data["name"]
        ).first():
            abort(
                400,
                message=f"There is already a tag named <{tag_data['name']}> for the store with id <{store_id}>",
            )

        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag


@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItems(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get(item_id)
        if not item:
            abort(400, message="No item was found with the provided id")

        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(400, message="No tag was found for the provided id")

        if item.store_id != tag.store_id:
            abort(
                400,
                message="It's not possible to associate tags and items from different stores",
            )

        has_relation = ItemsTagsModel.query.filter(
            ItemsTagsModel.item_id == item_id and ItemsTagsModel.tag_id == tag_id
        ).first()
        if has_relation:
            abort(
                404,
                message=f"Item <{item.name}> and tag <{tag.name}> are already related.",
            )

        # SQLAlchemy Trata as relações many-many como uma lista
        item.tags.append(tag)
        # OU tag.items.append(item)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, str(e))

        return tag

    @blp.response(200, ItemsTagsSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get(item_id)
        if not item:
            abort(400, message="No item was found with the provided id")

        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(400, message="No tag was found for the provided id")

        if item.store_id != tag.store_id:
            abort(
                400,
                message="It's not possible to associate tags and items from different stores",
            )

        # SQLAlchemy Trata as relações many-many como uma lista
        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, str(e))

        return {"message": "Item removed from tag", "item": item, "tag": tag}


@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        try:
            tag = TagModel.query.get(tag_id)
            if not tag:
                abort(404, message="No tag found for the provided tag_id")
            return tag
        except SQLAlchemyError:
            abort(500, message="Not able to retrieve data from our database")

    # Exemplo de várias tratativas de erro
    @blp.response(
        202,
        description="Deletes a tag if no item is tagged with it.",
        example={"message": "Tag deleted"},
    )
    @blp.alt_response(404, description="Tag not found")
    @blp.alt_response(
        400, description="Returned if the tag is linked to one or more Item"
    )
    def delete(self, tag_id):
        tag = TagModel.query.get(tag_id)

        if not tag:
            abort(404, message="No tag found for the provided tag_id")

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag Deleted"}

        abort(
            400,
            message="Could not delete tag. Make sure tag is not associated with any item.",
        )
