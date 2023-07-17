from db import db


class ItemModel(db.Model):
    __tablename__ = "items"

    # Columns
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    # FK aponta pra o __tablename__ da outra tabela e a sua PK
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("stores.store_id"),
        unique=False,
        nullable=False,
    )

    # Relations
    store = db.relationship("StoreModel", back_populates="items")
    tags = db.relationship("TagModel", back_populates="items", secondary="items_tags")
