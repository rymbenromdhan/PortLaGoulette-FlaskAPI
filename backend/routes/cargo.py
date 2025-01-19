from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_apispec import use_kwargs, marshal_with, doc
from marshmallow import Schema, fields
from models import Cargo
from app import db
from utils import role_required

cargo_bp = Blueprint('cargo', __name__)

# -------------------
# Marshmallow Schemas
# -------------------

class CargoRequestSchema(Schema):
    tracking_id = fields.Str(required=True, description="Unique tracking ID of the cargo")
    status = fields.Str(required=True, description="Current status of the cargo")

class CargoUpdateSchema(Schema):
    status = fields.Str(required=True, description="Updated status of the cargo")

class CargoResponseSchema(Schema):
    id = fields.Int()
    tracking_id = fields.Str()
    status = fields.Str()


# -------------------
# 1. Get Cargo by Tracking ID
# -------------------
@cargo_bp.route('/<int:tracking_id>', methods=['GET'])
@jwt_required()
@doc(description="Retrieve specific cargo details by tracking ID.", tags=["Cargo"])
@marshal_with(CargoResponseSchema, code=200)
def get_cargo(tracking_id):
    """
    Retrieve specific cargo details by tracking ID.
    """
    cargo = Cargo.query.filter_by(tracking_id=tracking_id).first()
    if not cargo:
        return {"error": "Cargo not found"}, 404
    return cargo


# -------------------
# 2. Add New Cargo
# -------------------
@cargo_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('editor')
@doc(description="Add new cargo information. Editors and above only.", tags=["Cargo"])
@use_kwargs(CargoRequestSchema, location="json")
@marshal_with(CargoResponseSchema, code=201)
def add_cargo(tracking_id, status):
    """
    Add new cargo information.
    """
    new_cargo = Cargo(tracking_id=tracking_id, status=status)
    db.session.add(new_cargo)
    db.session.commit()
    return new_cargo, 201


# -------------------
# 3. Update Cargo Status
# -------------------
@cargo_bp.route('/<int:tracking_id>', methods=['PUT'])
@jwt_required()
@role_required('editor')
@doc(description="Update the status of a cargo by tracking ID. Editors and above only.", tags=["Cargo"])
@use_kwargs(CargoUpdateSchema, location="json")
def update_cargo(tracking_id, status):
    """
    Update the status of a cargo by tracking ID.
    """
    cargo = Cargo.query.filter_by(tracking_id=tracking_id).first()
    if not cargo:
        return {"error": "Cargo not found"}, 404

    cargo.status = status
    db.session.commit()
    return {"message": "Cargo status updated successfully!"}, 200


# -------------------
# 4. Delete Cargo
# -------------------
@cargo_bp.route('/<int:tracking_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
@doc(description="Delete cargo by tracking ID. Admins only.", tags=["Cargo"])
def delete_cargo(tracking_id):
    """
    Delete cargo by tracking ID.
    """
    cargo = Cargo.query.filter_by(tracking_id=tracking_id).first()
    if not cargo:
        return {"error": "Cargo not found"}, 404

    db.session.delete(cargo)
    db.session.commit()
    return {"message": "Cargo deleted successfully!"}, 200

    # -------------------
# 5. Get All Cargo
# -------------------
@cargo_bp.route('/', methods=['GET'])
@jwt_required()
@doc(description="Retrieve a list of all cargo.", tags=["Cargo"])
@marshal_with(CargoResponseSchema(many=True), code=200)
def get_all_cargo():
    """
    Retrieve a list of all cargo.
    """
    cargo_list = Cargo.query.all()
    return cargo_list, 200

