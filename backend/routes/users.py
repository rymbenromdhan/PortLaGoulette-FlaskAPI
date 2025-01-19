from flask import Blueprint, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_apispec import use_kwargs, marshal_with, doc
from marshmallow import Schema, fields
from models import User
from app import db
from utils import role_required

bcrypt = Bcrypt()
users_bp = Blueprint('users', __name__)  # Blueprint for user routes

# Schemas for request and response validation/documentation
class UserRequestSchema(Schema):
    username = fields.Str(required=True, description="User's username")
    password = fields.Str(required=True, description="User's password")
    role = fields.Str(missing="viewer", description="Role assigned to the user (default: viewer)")

class UserResponseSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    role = fields.Str()

class RoleUpdateSchema(Schema):
    role = fields.Str(
        required=True,
        validate=lambda r: r in ["viewer", "admin", "editor"],
        description="The new role for the user. Allowed values: viewer, admin, editor.",
    )



# -------------------
# 1. Register a New User
# -------------------
@users_bp.route('/register', methods=['POST'])
@doc(description="Register a new user.", tags=['Users'])
@use_kwargs(UserRequestSchema, location="json")
@marshal_with(UserResponseSchema, code=201)
def register(username, password, role):
    """
    Register a new user.
    """
    if User.query.filter_by(username=username).first():
        return {"error": "Username already exists"}, 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    # Return the newly created user
    return {
        "id": new_user.id,
        "username": new_user.username,
        "role": new_user.role,
    }, 201
# -------------------
# 2. Log In a User
# -------------------
@users_bp.route('/login', methods=['POST'])
@doc(description="Authenticate a user and return a JWT token.", tags=['Users'])
@use_kwargs(UserRequestSchema(only=("username", "password")), location="json")
def login(username, password):
    """
    Authenticate user and return a JWT token.
    """
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return {"error": "Invalid username or password"}, 401

    access_token = create_access_token(identity=str(user.id))
    return {"access_token": access_token}, 200

# -------------------
# 3. Get User by ID (Admin Only)
# -------------------
@users_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@role_required('admin')
@doc(description="Retrieve user details by ID. Admins only.", tags=['Users'])
@marshal_with(UserResponseSchema, code=200)
def get_user(id):
    """
    Retrieve user details by ID.
    """
    user = User.query.get(id)
    if not user:
        return {"error": "User not found"}, 404

    # Return the user details
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }, 200


# -------------------
# 4. Delete a User (Admin Only)
# -------------------
@users_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
@doc(description="Delete a user by ID. Admins only.", tags=['Users'])
def delete_user(id):
    """
    Delete a user account by ID.
    """
    user = User.query.get(id)
    if not user:
        return {"error": "User not found"}, 404

    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted successfully!"}, 200


# -------------------
# 5. Update User Role (Admin Only)
# -------------------
@users_bp.route('/<int:id>/role', methods=['PUT'])
@jwt_required()
@role_required('admin')
@doc(description="Update a user's role by ID. Admins only.", tags=['Users'])
@use_kwargs(RoleUpdateSchema, location="json")
def update_user_role(id, role):
    """
    Update a user's role by ID.
    """
    user = User.query.get(id)
    if not user:
        return {"error": "User not found"}, 404

    user.role = role
    db.session.commit()
    return {"message": f"User role updated to '{role}' successfully!"}, 200
