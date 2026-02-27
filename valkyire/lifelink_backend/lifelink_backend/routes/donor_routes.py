from flask import Blueprint, request, jsonify
from models.donor_model import Donor

donor_bp = Blueprint("donor_bp", __name__)

donors_list = []

@donor_bp.route("/register", methods=["POST"])
def register_donor():
    data = request.json

    donor = Donor(
        data["name"],
        data["blood_type"],
        float(data["latitude"]),
        float(data["longitude"])
    )

    donors_list.append(donor)

    return jsonify({"message": "Donor registered successfully"})