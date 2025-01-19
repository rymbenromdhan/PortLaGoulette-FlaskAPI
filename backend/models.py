from app import db

class Vessel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    schedule = db.Column(db.String(200), nullable=False)

class Cargo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')  # Default role is "viewer"


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_allocated = db.Column(db.Boolean, default=False)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vessel_id = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())