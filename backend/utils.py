from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from functools import wraps
from models import User

def role_required(required_role):
    """
    A decorator to enforce role-based access control.
    :param required_role: The role required to access the endpoint.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            if user.role != required_role:
                return jsonify({"error": f"Access denied: Requires '{required_role}' role"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
