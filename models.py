from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
  id = db.Column(db.String(), primary_key=True)
  firstname = db.Column(db.String(), nullable=False)
  lastname = db.Column(db.String(), nullable=False)
  number = db.Column(db.String(), nullable=False)
  whatsapp = db.Column(db.String(), nullable=True)
  password = db.Column(db.String(), nullable=False)
  role = db.Column(db.String(), default="user")
  is_admin = db.Column(db.Boolean(), default=False)
  last_active = db.Column(db.DateTime, default=datetime.utcnow)
  listings = db.relationship("Item", backref='user')


class Item(db.Model):
  id = db.Column(db.String, primary_key=True)
  brand = db.Column(db.String, nullable=False)
  model = db.Column(db.String, nullable=False)
  price = db.Column(db.Integer, nullable=False)
  type = db.Column(db.String, nullable=False)
  country = db.Column(db.String, nullable=False)
  region = db.Column(db.String, nullable=False)
  description = db.Column(db.String, nullable=False)
  publisher_id = db.Column(db.String, db.ForeignKey('user.id'))
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  is_featured = db.Column(db.Boolean(), default=False)
  images = db.relationship("ItemImages", backref='item')

class ItemImages(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  filename = db.Column(db.String(), nullable=False)
  itemId = db.Column(db.String(), db.ForeignKey('item.id'))

class Countries(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  code = db.Column(db.String, nullable=False)
  regions = db.relationship("Regions", backref='country')

class Regions(db.Model):
  id =db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  countryId = db.Column(db.Integer, db.ForeignKey('countries.id'))
