"""Models for Shopify Inventory System"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DEFAULT_IMAGE = "./static/images/box.jpg"


class Item(db.Model):
    """Item tracked by Shopify Inventory System"""

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.Text, nullable=False, default=DEFAULT_IMAGE)
    deleted = db.Column(db.Boolean, nullable=False, default=False)
    msg = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """Serialize Item to a dict of Item info"""

        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "image": self.image,
            "deleted": self.deleted,
            "msg": self.msg,
        }


def connect_db(app):
    """Connect to database"""

    db.app = app
    db.init_app(app)
