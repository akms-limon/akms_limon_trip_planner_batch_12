from flask import Blueprint, jsonify, request
from app.services import (
    create_trip,
    get_all_trips,
    get_trip_by_id,
    update_trip,
    delete_trip,
    add_traveler,
    remove_traveler
)
from app.validators import validate_trip_data, validate_traveler_data
from app.utils import trip_to_dict


main_bp = Blueprint("main", __name__)
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")



@main_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@api_bp.route("/trips", methods=["POST"])
def create_trip_route():
    data = request.get_json(silent=True)

    cleaned_data, error = validate_trip_data(data)

    if error:
        return jsonify({"error": error}), 400
    trip = create_trip(cleaned_data)

    return jsonify(trip_to_dict(trip)), 201


@api_bp.route("/trips", methods=["GET"])
def get_trips():
    trips = get_all_trips()

    response = []
    for trip in trips:
        response.append(trip_to_dict(trip))

    return jsonify(response), 200


@api_bp.route("/trips/<int:trip_id>", methods=["GET"])
def get_trip(trip_id):
    trip = get_trip_by_id(trip_id)

    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    return jsonify(trip_to_dict(trip)), 200

@api_bp.route("/trips/<int:trip_id>", methods=["PUT"])
def update_trip_route(trip_id):
    trip = get_trip_by_id(trip_id)

    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    data = request.get_json(silent=True)
    cleaned_data, error = validate_trip_data(data)
    if error:
        return jsonify({"error": error}), 400
    
    trip = update_trip(trip, cleaned_data)

    return jsonify(trip_to_dict(trip)), 200


@api_bp.route("/trips/<int:trip_id>", methods=["DELETE"])
def delete_trip_route(trip_id):
    trip = get_trip_by_id(trip_id)

    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    delete_trip(trip)

    return jsonify({"message": "Trip deleted successfully"}), 200



@api_bp.route("/trips/<int:trip_id>/travelers", methods=["POST"])
def add_traveler_route(trip_id):
    trip = get_trip_by_id(trip_id)

    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    data = request.get_json(silent=True)
    cleaned_data, error = validate_traveler_data(data)
    if error:
        return jsonify({"error": error}), 400

    traveler, error_code, error_message = add_traveler(
        trip,
        cleaned_data,
    )
    if error_code:
        return jsonify({
            "error": error_code,
            "message": error_message,
        }), 409

    return jsonify({
        "id": traveler.id,
        "name": traveler.name,
        "email": traveler.email,
    }), 201


@api_bp.route("/trips/<int:trip_id>/travelers/<int:traveler_id>", methods=["DELETE"])
def remove_traveler_route(trip_id, traveler_id):
    trip = get_trip_by_id(trip_id)

    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    traveler, error_code, error_message = remove_traveler(
        trip,
        traveler_id,
    )
    if error_code:
        status_code = 404 if error_code == "TRAVELER_NOT_FOUND" else 409
        return jsonify({
            "error": error_code,
            "message": error_message,
        }), status_code

    return jsonify({
        "message": "Traveler removed successfully"
    }), 200