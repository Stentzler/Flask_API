from db import db


class TagModel(db.Model):
    __tablename__ = "tags"

    # Columns
    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("stores.store_id"),
        unique=False,
        nullable=False,
    )

    # Relations
    store = db.relationship("StoreModel", back_populates="tags")
    items = db.relationship("ItemModel", back_populate="tags", secondary="items_tags")
