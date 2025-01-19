from apispec import APISpec
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flasgger import Swagger
from dotenv import load_dotenv
from flask_apispec import FlaskApiSpec
from apispec.ext.marshmallow import MarshmallowPlugin
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///port.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'supersecretkey')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# APISpec configuration for Swagger
app.config.update({
    'APISPEC_SPEC': APISpec(
        title="Port La Goulette Smart Port Management System API",
        version="1.0.0",
        plugins=[MarshmallowPlugin()],
        openapi_version="3.0.0",
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # Swagger JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/',  # Swagger UI
})

# Initialize FlaskApiSpec
docs = FlaskApiSpec(app)

# Root route
@app.route('/')
def home():
    """
    Welcome to the Smart Port Management System API.
    ---
    responses:
      200:
        description: A welcome message for the API.
    """
    return jsonify({"message": "Welcome to the Port La Goulette Smart Port Management System API!"})

# Import blueprints and route functions
from routes.resources import allocate_resource, get_resources
from routes.users import (
    users_bp,
    register,
    login,
    get_user,
    delete_user,
    update_user_role,
)

from routes.vessels import (
    vessels_bp,
    get_vessels,
    add_vessel,
    update_vessel,
    delete_vessel,
)


# Register blueprints
app.register_blueprint(users_bp, url_prefix='/users')

# Register routes for documentation
docs.register(register, blueprint='users')
docs.register(login, blueprint='users')
docs.register(get_user, blueprint='users')
docs.register(delete_user, blueprint='users')
docs.register(update_user_role, blueprint='users')

# Register blueprint
app.register_blueprint(vessels_bp, url_prefix='/vessels')

# Register routes for documentation
docs.register(get_vessels, blueprint='vessels')
docs.register(add_vessel, blueprint='vessels')
docs.register(update_vessel, blueprint='vessels')
docs.register(delete_vessel, blueprint='vessels')

from routes.cargo import (
    cargo_bp,
    get_cargo,
    add_cargo,
    update_cargo,
    delete_cargo,
)

# Register blueprint
app.register_blueprint(cargo_bp, url_prefix='/cargo')

# Register routes for documentation
docs.register(get_cargo, blueprint='cargo')
docs.register(add_cargo, blueprint='cargo')
docs.register(update_cargo, blueprint='cargo')
docs.register(delete_cargo, blueprint='cargo')

from routes.environment import (
    environment_bp,
    get_environment_metrics,
    get_environmental_alerts,
)

# Register blueprint
app.register_blueprint(environment_bp, url_prefix='/environment')

# Register routes for documentation
docs.register(get_environment_metrics, blueprint='environment')
docs.register(get_environmental_alerts, blueprint='environment')

from routes.services import (
    services_bp,
    get_services,
    add_service_request,
)

# Register blueprint
app.register_blueprint(services_bp, url_prefix='/services')

from routes.resources import resources_bp, get_resources, allocate_resource


# Register routes for documentation
docs.register(get_services, blueprint='services')
docs.register(add_service_request, blueprint='services')

# Register blueprint
app.register_blueprint(resources_bp, url_prefix='/resources')

# Register routes for documentation
docs.register(get_resources, blueprint='resources')
docs.register(allocate_resource, blueprint='resources')


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
