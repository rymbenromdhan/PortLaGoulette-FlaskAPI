from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_apispec import use_kwargs, marshal_with, doc
from marshmallow import Schema, fields
from models import Service, ServiceRequest
from app import db
from utils import role_required

services_bp = Blueprint('services', __name__)

# -------------------
# Marshmallow Schemas
# -------------------

class ServiceResponseSchema(Schema):
    id = fields.Int(description="Service ID")
    name = fields.Str(description="Service name")
    description = fields.Str(description="Service description")

class ServiceRequestSchema(Schema):
    vessel_id = fields.Int(required=True, description="ID of the vessel requesting the service")
    service_id = fields.Int(required=True, description="ID of the service being requested")

class ServiceRequestResponseSchema(Schema):
    id = fields.Int(description="Service Request ID")
    vessel_id = fields.Int(description="ID of the vessel")
    service_id = fields.Int(description="ID of the requested service")
    status = fields.Str(description="Request status", default="Pending")


# -------------------
# 1. Get All Services
# -------------------
@services_bp.route('/', methods=['GET'])
@jwt_required()
@doc(description="Lists all available port services.", tags=["Services"])
@marshal_with(ServiceResponseSchema(many=True), code=200)
def get_services():
    """
    Lists all available port services.
    """
    services = Service.query.all()
    if not services:
        return []
    return services


# -------------------
# 2. Add a Service Request
# -------------------
@services_bp.route('/request', methods=['POST'])
@jwt_required()
@role_required('operator')  # Only users with the 'operator' role can make service requests
@doc(description="Handles service requests for vessels. Only 'operator' role users are allowed.", tags=["Services"])
@use_kwargs(ServiceRequestSchema, location="json")
@marshal_with(ServiceRequestResponseSchema, code=201)
def add_service_request(vessel_id, service_id):
    """
    Handles service requests for vessels.
    """
    # Validate service existence
    service = Service.query.get(service_id)
    if not service:
        return {"error": f"Service with ID {service_id} not found."}, 404

    # Create and save the service request
    service_request = ServiceRequest(vessel_id=vessel_id, service_id=service_id)
    db.session.add(service_request)
    db.session.commit()

    return service_request, 201
