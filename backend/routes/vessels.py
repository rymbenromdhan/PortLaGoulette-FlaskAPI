from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_apispec import use_kwargs, marshal_with, doc
from marshmallow import Schema, fields
from models import Vessel
from app import db
from utils import role_required

vessels_bp = Blueprint('vessels', __name__)

# -------------------
# Marshmallow Schemas
# -------------------

class VesselRequestSchema(Schema):
    name = fields.Str(required=True, description="Name of the vessel")
    schedule = fields.Str(required=True, description="Schedule for the vessel (e.g., '2025-01-20 08:00')")

class VesselResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    schedule = fields.Str()


# -------------------
# 1. Get All Vessels
# -------------------
@vessels_bp.route('/', methods=['GET'])
@jwt_required()
@doc(description="Retrieve all vessels.", tags=["Vessels"])
@marshal_with(VesselResponseSchema(many=True), code=200)
def get_vessels():
    """
    Get all vessels
    """
    vessels = Vessel.query.all()
    return vessels


# -------------------
# 2. Add a New Vessel
# -------------------
@vessels_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('editor')
@doc(description="Add a new vessel. Editors and above only.", tags=["Vessels"])
@use_kwargs(VesselRequestSchema, location="json")
@marshal_with(VesselResponseSchema, code=201)
def add_vessel(name, schedule):
    """
    Add a new vessel
    """
    new_vessel = Vessel(name=name, schedule=schedule)
    db.session.add(new_vessel)
    db.session.commit()
    return new_vessel, 201


# -------------------
# 3. Update a Vessel
# -------------------
@vessels_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required('editor')
@doc(description="Update a vessel. Editors and above only.", tags=["Vessels"])
@use_kwargs(VesselRequestSchema, location="json")
def update_vessel(id, name, schedule):
    """
    Update vessel details
    """
    vessel = Vessel.query.get(id)
    if not vessel:
        return {"error": "Vessel not found"}, 404

    vessel.name = name
    vessel.schedule = schedule
    db.session.commit()
    return {"message": "Vessel updated successfully!"}, 200


# -------------------
# 4. Delete a Vessel
# -------------------
@vessels_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
@doc(description="Delete a vessel. Admins only.", tags=["Vessels"])
def delete_vessel(id):
    """
    Delete a vessel
    """
    vessel = Vessel.query.get(id)
    if not vessel:
        return {"error": "Vessel not found"}, 404

    db.session.delete(vessel)
    db.session.commit()
    return {"message": "Vessel deleted successfully!"}, 200
