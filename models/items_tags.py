from db import db


# Many_to_Many
class ItemsTagsModel(db.Model):
    __tablename__ = "items_tags"

    # Columns
    items_tags_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.item_id"), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.tag_id"), nullable=False)
