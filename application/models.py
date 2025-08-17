from .database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer(), primary_key =True)
    username = db.Column(db.String(), unique = True, nullable =False)   
    password = db.Column(db.String(),  nullable =False)
    fullname = db.Column(db.String() , nullable =False)
    address = db.Column(db.String() , nullable =False)
    pincode = db.Column(db.String(), nullable =False)
    type = db.Column(db.String(), default="user") 
    reservations = db.relationship("Reservation", backref ="user")

class ParkingLot(db.Model):
    id = db.Column(db.Integer() , primary_key =True)
    prime_location_name = db.Column(db.String(), nullable =False)
    price = db.Column(db.Float(), nullable=False)
    address = db.Column(db.String(), nullable = False)
    pincode = db.Column(db.String(), nullable =False)
    max_spots = db.Column(db.Integer(), nullable =False)
    spots = db.relationship("ParkingSpot", backref="lot")

class ParkingSpot(db.Model):
    id = db.Column(db.Integer(), primary_key =True)
    lot_id = db.Column(db.Integer(), db.ForeignKey("parking_lot.id"), nullable =False)
    status = db.Column(db.String(), default="available", nullable=False)
    reservations = db.relationship("Reservation", backref="spot")

class Reservation(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    spot_id = db.Column(db.Integer(), db.ForeignKey("parking_spot.id"), nullable =False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable= False)
    parking_timestamp = db.Column(db.DateTime(), default =datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime())
    cost_per_unit = db.Column(db.Float())
    vehicle_number = db.Column(db.String(), nullable =False)

