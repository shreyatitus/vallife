from utils.haversine import calculate_distance
from services.cooldown_service import is_eligible
from config import MAX_DISTANCE_KM

def find_best_donor(request_blood_type, req_lat, req_lon, donors):

    eligible_donors = []

    for donor in donors:
        if donor.blood_type == request_blood_type and is_eligible(donor):

            distance = calculate_distance(
                req_lat, req_lon,
                donor.latitude, donor.longitude
            )

            if distance <= MAX_DISTANCE_KM:
                eligible_donors.append((donor, distance))

    eligible_donors.sort(key=lambda x: x[1])

    if eligible_donors:
        return eligible_donors[0][0]

    return None