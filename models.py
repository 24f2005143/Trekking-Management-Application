from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role = db.Column(db.String(20), nullable=False)  
    is_blacklisted = db.Column(db.Boolean, default=False)

    bookings = db.relationship('Booking', backref='user', lazy=True)
    staff_profile = db.relationship('StaffProfile', backref='user', uselist=False)


class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phone = db.Column(db.String(20))
    experience = db.Column(db.String(100))
    status = db.Column(db.String(20), default="Active")

    treks = db.relationship('Trek', backref='staff', lazy=True, cascade="all, delete")


class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))           
    difficulty = db.Column(db.String(20))
    duration = db.Column(db.Integer, nullable=True)
    available_slots = db.Column(db.Integer, default=10)
    status = db.Column(db.String(20), default="Open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    staff_id = db.Column(db.Integer, db.ForeignKey('staff_profile.id'))

    bookings = db.relationship('Booking', backref='trek', lazy=True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)

    booking_status = db.Column(db.String(20), default="Booked")
    payment_status = db.Column(db.String(20), default="Pending")
