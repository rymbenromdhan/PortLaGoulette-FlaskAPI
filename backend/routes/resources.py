from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_apispec import doc, use_kwargs, marshal_with
from marshmallow import Schema, fields
from app import db
from utils import role_required
from models import Resource  # Ensure this model exists in your project

resources_bp = Blueprint('resources', __name__)

# -------------------
# Marshmallow Schemas
# -------------------

class ResourceResponseSchema(Schema):
    id = fields.Int(description="Resource ID")
    name = fields.Str(description="Name of the resource")
    is_allocated = fields.Bool(description="Whether the resource is currently allocated")

class ResourceAllocateSchema(Schema):
    resource_id = fields.Int(required=True, description="ID of the resource to allocate")


# -------------------
# 1. Get All Resources
# -------------------
@resources_bp.route('/', methods=['GET'])
@jwt_required()
@doc(description="Display available resources.", tags=["Resources"])
@marshal_with(ResourceResponseSchema(many=True), code=200)
def get_resources():
    """
    Display available resources.
    """
    resources = Resource.query.all()
    if not resources:
        return []
    return resources


# -------------------
# 2. Allocate a Resource
# -------------------
@resources_bp.route('/allocate', methods=['POST'])
@jwt_required()
@role_required('operator')  # Only 'operator' role can allocate resources
@doc(description="Allocate a resource for an operation. Only 'operator' role users are allowed.", tags=["Resources"])
@use_kwargs(ResourceAllocateSchema, location="json")
def allocate_resource(resource_id):
    """
    Allocate a resource for an operation.
    """
    # Fetch the resource by ID
    resource = Resource.query.get(resource_id)
    if not resource:
        return {"error": "Resource not found"}, 404

    if resource.is_allocated:
        return {"error": "Resource is already allocated"}, 400

    resource.is_allocated = True
    db.session.commit()
    return {"message": f"Resource '{resource.name}' allocated successfully!"}, 200
