from app import app
from models import db, Item

db.drop_all()
db.create_all()

i1 = Item(
    name='Expensive graphics card',
    price=700,
)

i2 = Item(
    name='Bananas',
    price=5,
)

db.session.add_all([i1, i2])
db.session.commit()
