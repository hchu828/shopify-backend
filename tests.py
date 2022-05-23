from unittest import TestCase

from app import app
from models import db, Item

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///shopify-inventory-test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()

ITEM_DATA = {
    "name": "Expensive cookies",
    "price": 140213,
    "image": "fakeImage"
}

ITEM_DATA_2 = {
    "name": "Plastic spoon",
    "price": 2,
    "image": "fakeImage2"
}


class ItemViewsTestCase(TestCase):
    """Tests for views of API"""

    def setUp(self):
        """Make demo data"""

        Item.query.delete()

        item = Item(**ITEM_DATA)
        db.session.add(item)
        db.session.commit()

        self.item = item

    def tearDown(self):
        """Clean up fouled transactions"""

        db.session.rollback()

    def test_list_items(self):
        with app.test_client() as client:
            resp = client.get("/items")

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertEqual(data, {
                "items": [{
                    "id": self.item.id,
                    "name": "Expensive cookies",
                    "price": 140213,
                    "image": "fakeImage",
                    "deleted": False,
                    "msg": None
                }]
            })

    def test_get_item(self):
        with app.test_client() as client:
            url = f"/items/{self.item.id}"
            resp = client.get(url)

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertEqual(data, {
                "item": {
                    "id": self.item.id,
                    "name": "Expensive cookies",
                    "price": 140213,
                    "image": "fakeImage",
                    "deleted": False,
                    "msg": None
                }
            })

    def test_create_item(self):
        with app.test_client() as client:
            resp = client.post("/items", json=ITEM_DATA_2)

            self.assertEqual(resp.status_code, 201)

            data = resp.json.copy()

            self.assertIsInstance(data['item']['id'], int)
            del data['item']['id']

            self.assertEqual(data, {
                "item": {
                    "name": "Plastic spoon",
                    "price": 2,
                    "image": "fakeImage2",
                    "deleted": False,
                    "msg": None
                }
            })

    def test_update_item(self):
        with app.test_client() as client:
            url = f"/items/{self.item.id}"
            resp = client.patch(url, json=ITEM_DATA_2)

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertEqual(data, {
                "item": {
                    "id": self.item.id,
                    "name": "Plastic spoon",
                    "price": 2,
                    "image": "fakeImage2",
                    "deleted": False,
                    "msg": None
                }
            })

    def test_soft_delete(self):
        with app.test_client() as client:
            url = f"/items/{self.item.id}/softdelete"
            resp = client.patch(url, json={"msg" : "Bye", "id": self.item.id})

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertEqual(data, {
                "item": {
                    "id": self.item.id,
                    "name": "Expensive cookies",
                    "price": 140213,
                    "image": "fakeImage",
                    "deleted": True,
                    "msg": "Bye",
                }
            })

    def test_soft_undelete(self):
        with app.test_client() as client:
            "Delete then undelete"
            url = f"/items/{self.item.id}/softdelete"
            resp = client.patch(url, json={"msg" : "Bye", "id": self.item.id})

            url = f"/items/{self.item.id}/undelete"
            resp = client.patch(url, json={"id": self.item.id})

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertEqual(data, {
                "item": {
                    "id": self.item.id,
                    "name": "Expensive cookies",
                    "price": 140213,
                    "image": "fakeImage",
                    "deleted": False,
                    "msg": None,
                }
            })

    def test_hard_delete(self):
        with app.test_client() as client:
            url = f"/items/{self.item.id}"
            resp = client.delete(url)

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertEqual(data, {"deleted": self.item.id})
