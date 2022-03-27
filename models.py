from sqlalchemy.orm import backref
from app import db

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    items = db.relationship("MenuItem", backref="restaurant")

    def __init__(self, name):
        self.name = name

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    description = db.Column(db.String())
    price = db.Column(db.Float())
    ingredients = db.Column(db.ARRAY(db.String()))

    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"))

    def __init__(self, name, description, price, ingredients):
        self.name = name
        self.description = description
        self.price = price
        self.ingredients = ingredients
