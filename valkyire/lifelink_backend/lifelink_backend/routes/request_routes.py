from flask import Blueprint, request, jsonify
from routes.donor_routes import donors_list
from services.matching_service import find_best_donor

request_bp = Blueprint("request_bp", __name__)

@request_bp.route("/request-blood", methods=["POST"])
def request_blood():

    data = request.json

    matched = find_best_donor(
        data["blood_type"],
        float(data["latitude"]),
        float(data["longitude"]),
        donors_list
    )

    if matched:
        return jsonify({
            "message": "Donor Found",
            "name": matched.name,
            "points": matched.points
        })

    return jsonify({"message": "No eligible donor found"})