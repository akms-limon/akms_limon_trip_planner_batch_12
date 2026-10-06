from flask import Blueprint, jsonify, request

from app.services import create_trip
from app.validators import validate_trip_data

main_bp = Blueprint("main", __name__)


@main_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@main_bp.route("/api/v1/trips", methods=["POST"])
def create_trip_route():
    data = request.get_json(silent=True)

    cleaned_data, error = validate_trip_data(data)

    if error:
        return jsonify({"error": error}), 400

    trip = create_trip(cleaned_data)

    response = {
        "id": trip.id,
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat(),
        "end_date": trip.end_date.isoformat(),
        "budget": trip.budget,
        "max_travelers": trip.max_travelers,
        "status": trip.status,
    }

    return jsonify(response), 201