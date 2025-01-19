import requests
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_apispec import doc, marshal_with
from marshmallow import Schema, fields
from utils import role_required
import logging

environment_bp = Blueprint('environment', __name__)

# Replace with your actual WeatherAPI key
WEATHER_API_KEY = 'ef1d406aca01419e90d154339242912'
BASE_URL = "https://api.weatherapi.com/v1"  # Fixed the URL

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# -------------------
# Marshmallow Schemas
# -------------------

class EnvironmentMetricsSchema(Schema):
    temperature = fields.Float(description="Current temperature in Celsius")
    humidity = fields.Int(description="Current humidity percentage")
    wind_speed = fields.Float(description="Current wind speed in kph")
    visibility = fields.Float(description="Current visibility in km")

class EnvironmentalAlertsSchema(Schema):
    alerts = fields.List(fields.Str, description="List of environmental alerts")


# -------------------
# 1. Get Environment Metrics
# -------------------
@environment_bp.route('/', methods=['GET'])
@jwt_required()
@doc(description="Provides data on environmental metrics using WeatherAPI.", tags=["Environment"])
@marshal_with(EnvironmentMetricsSchema, code=200)
def get_environment_metrics():
    """
    Provides data on environmental metrics using WeatherAPI.
    """
    try:
        response = requests.get(f"{BASE_URL}/current.json", params={
            "key": WEATHER_API_KEY,
            "q": "Port La Goulette"
        }, timeout=10)  # Added timeout for the request

        # Log the full response for debugging
        logging.debug(f"Request URL: {response.url}")
        logging.debug(f"Response Status: {response.status_code}")
        logging.debug(f"Response Body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            return {
                "temperature": data['current']['temp_c'],
                "humidity": data['current']['humidity'],
                "wind_speed": data['current']['wind_kph'],
                "visibility": data['current']['vis_km']
            }
        else:
            return {"error": f"Failed to fetch environmental data. Status Code: {response.status_code}"}, 500

    except requests.exceptions.RequestException as e:
        logging.error(f"Request to WeatherAPI failed: {e}")
        return {"error": "An error occurred while fetching environmental data."}, 500


# -------------------
# 2. Get Environmental Alerts
# -------------------
@environment_bp.route('/alerts', methods=['GET'])
@jwt_required()
@role_required('admin')
@doc(description="Fetches safety and environmental alerts based on weather conditions.", tags=["Environment"])
@marshal_with(EnvironmentalAlertsSchema, code=200)
def get_environmental_alerts():
    """
    Fetches safety and environmental alerts based on weather conditions.
    """
    try:
        response = requests.get(f"{BASE_URL}/current.json", params={
            "key": WEATHER_API_KEY,
            "q": "Port La Goulette"
        }, timeout=10)  # Added timeout for the request

        # Log the full response for debugging
        logging.debug(f"Request URL: {response.url}")
        logging.debug(f"Response Status: {response.status_code}")
        logging.debug(f"Response Body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            alerts = []

            # Generate alerts based on weather conditions
            wind_speed = data['current']['wind_kph']
            temperature = data['current']['temp_c']
            if wind_speed > 50:
                alerts.append(f"High wind speed: {wind_speed} kph")
            if temperature > 40:
                alerts.append("Heatwave warning")
            if not alerts:
                alerts.append("No significant weather alerts")

            return {"alerts": alerts}
        else:
            return {"error": f"Failed to fetch environmental data. Status Code: {response.status_code}"}, 500

    except requests.exceptions.RequestException as e:
        logging.error(f"Request to WeatherAPI failed: {e}")
        return {"error": "An error occurred while fetching environmental alerts."}, 500
