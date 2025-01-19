from app import db

def initialize_db():
    db.create_all()
