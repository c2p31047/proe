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
    altitude = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Shelter {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
        }