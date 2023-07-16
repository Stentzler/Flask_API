from db import db


class TagModel(db.Model):
    __tablename__ = "tags"

    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("stores.store_id"),
        unique=False,
        nullable=False,
    )
    store = db.relationship("StoreModel", back_populates="tags")
