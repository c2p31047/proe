from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(150))
    shelter_id = db.Column(db.Integer)
    work_address = db.Column(db.String(150))
    work_shelter_id = db.Column(db.Integer)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    phonenumber = db.Column(db.String(20))

    def is_admin(self):
        return Admin.query.filter_by(email=self.email).first() is not None

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    permission = db.Column(db.Integer, default=0)

class Shelter(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer, server_default='')
    flood = db.Column(db.Integer)
    landslide = db.Column(db.Integer)
    hightide = db.Column(db.Integer)
    earthquake = db.Column(db.Integer)
    tsunami = db.Column(db.Integer)
    fire = db.Column(db.Integer)
    inland_flooding = db.Column(db.Integer)
    volcano = db.Column(db.Integer)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float)
    other = db.Column(db.String(255))

    def __repr__(self):
        return f"<Shelter {self.name}>"

    def to_dict(self): #JSONに変換するためのもの
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'capacity': self.capacity,
            'other': self.other,
        }

class AdminShelter(db.Model):
    __tablename__ = 'admin_shelter'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelter.id'), nullable=False)

class Population(db.Model):
    __tablename__ = 'population'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    areaname = db.Column(db.String(255), nullable=False)
    agegroup = db.Column(db.String(255), nullable=False)
    population = db.Column(db.Integer, nullable=False)

class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelter.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('stock_category.id'), nullable=True)
    stockname = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    note = db.Column(db.Text, nullable=True)
    expiration = db.Column(db.Date, nullable=True)
    condition = db.Column(db.Text, nullable=True)

    shelter = db.relationship('Shelter', backref='stocks')
    category = db.relationship('StockCategory', backref='stocks')


class StockActivity(db.Model):
    __tablename__ = 'stock_activity'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelter.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    type = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=False)
    content = db.Column(db.Text, nullable=True)
    other = db.Column(db.Text, nullable=True)

class StockCategory(db.Model):
    __tablename__ = 'stock_category'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    other = db.Column(db.Text, nullable=False)