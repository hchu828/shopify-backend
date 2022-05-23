"""Flask app for Shopify Inventory System"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from models import db, connect_db, Item, DEFAULT_IMAGE

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///shopify-inventory'
app.config['SQLALCHEMY_TRACK_MODFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-shopify-system'
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)


@app.get("/")
def root():
    """Render homepage."""

    return render_template("index.html")


@app.get("/items")
def get_items():
    """Return items in system, with optional filtering.

    Returns JSON like:
        {items: [{id, name, price, image}, ...]}
    """

    filter = request.args.get("filter")

    if filter == "current":
        items = [
            item.to_dict() for item in Item.query.filter_by(deleted=False)]

    elif filter == "deleted":
        items = [
            item.to_dict() for item in Item.query.filter_by(deleted=True)]

    else:
        items = [item.to_dict() for item in Item.query.all()]

    return jsonify(items=items)


@app.get("/items/<int:item_id>")
def get_item(item_id):
    """Return data on specific item.

    Returns JSON like:
        {item: [{id, name, price, image, deleted}]}
    """

    item = Item.query.get_or_404(item_id)
    return jsonify(item=item.to_dict())


@app.post("/items")
def create_item():
    """Add item, and return data about newly-created item.

    Returns JSON like:
        {item: [{id, name, price, image}]}
    """

    data = request.json

    item = Item(
        name=data['name'],
        price=data['price'],
        image=data['image'] or None
    )

    db.session.add(item)
    db.session.commit()

    return (jsonify(item=item.to_dict()), 201)


@app.patch("/items/<int:item_id>")
def update_item(item_id):
    """Update item from data in request. Return updated data.

    Returns JSON like:
        {item: [{id, name, price, image, deleted}]}
    """

    data = request.json
    item = Item.query.get_or_404(item_id)

    item.name = data.get('name', item.name)
    item.price = data.get('price', item.price)

    if "image" in data:
        item.image = data['image'] or DEFAULT_IMAGE

    db.session.add(item)
    db.session.commit()

    return jsonify(item=item.to_dict())


@app.patch("/items/<int:item_id>/softdelete")
def soft_delete(item_id):
    """Flag item as deleted and store delete comment in msg.

    Returns JSON like:
        {item: [{id, name, price, image, deleted, msg}]}
    """

    data = request.json
    item = Item.query.get_or_404(item_id)

    item.deleted = True
    item.msg = data['msg']

    db.session.add(item)
    db.session.commit()

    return jsonify(item=item.to_dict())


@app.patch("/items/<int:item_id>/undelete")
def soft_undelete(item_id):
    """Flag item as undeleted and removes msg field from db.

    Returns JSON like:
        {item: [{id, name, price, image, deleted}]}
    """

    item = Item.query.get_or_404(item_id)

    item.deleted = False
    item.msg = None

    db.session.add(item)
    db.session.commit()

    return jsonify(item=item.to_dict())


@app.delete("/items/<int:item_id>")
def hard_delete(item_id):
    """Hard deletes a soft-deleted item. Item is permanently removed
    and cannto be recovered.

    Returns JSON like: {msg: "Deleted"}
    """

    item = Item.query.get_or_404(item_id)

    db.session.delete(item)
    db.session.commit()

    return jsonify(deleted=item_id)
