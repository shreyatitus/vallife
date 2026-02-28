from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2

COOLDOWN_DAYS = 90

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    R = 6371  # Earth radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def check_cooldown_eligibility(last_donation_date):
    """Check if donor is eligible based on cooldown period"""
    if not last_donation_date:
        return True
    
    days_since_donation = (datetime.now() - last_donation_date).days
    return days_since_donation >= COOLDOWN_DAYS

def match_donors(db, blood_type, request_lat, request_lon):
    """
    AI Agent: Match donors for blood request
    Returns ranked list of eligible donors
    """
    # Step 1: Filter by blood group
    users = db.collection("users").where("blood", "==", blood_type).where("status", "==", "approved").stream()
    
    eligible_donors = []
    
    for user in users:
        user_data = user.to_dict()
        user_data["id"] = user.id
        
        # Step 2: Check cooldown eligibility
        last_donation = user_data.get("lastDonation")
        if last_donation:
            last_donation = datetime.fromisoformat(str(last_donation))
        
        if not check_cooldown_eligibility(last_donation):
            continue
        
        # Step 3: Calculate distance
        donor_lat = user_data.get("latitude", 0)
        donor_lon = user_data.get("longitude", 0)
        distance = haversine_distance(request_lat, request_lon, donor_lat, donor_lon)
        
        eligible_donors.append({
            "id": user_data["id"],
            "name": user_data["name"],
            "email": user_data["email"],
            "phone": user_data.get("phone", ""),
            "distance": round(distance, 2),
            "points": user_data.get("points", 0)
        })
    
    # Step 4: Rank by distance (nearest first)
    eligible_donors.sort(key=lambda x: x["distance"])
    
    return eligible_donors

def notify_donor(db, donor_id, request_id, request_data, donor_email):
    """Create notification for donor and send email"""
    from services.email_service import send_email
    
    notification = {
        "donor_id": donor_id,
        "request_id": request_id,
        "patient_name": request_data["patientName"],
        "blood_type": request_data["blood"],
        "hospital": request_data["hospital"],
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    db.collection("notifications").add(notification)
    
    # Send email
    subject = f"Urgent: Blood Donation Request - {request_data['blood']} Type"
    body = f"""Dear Donor,

A patient urgently needs your help!

Patient Name: {request_data['patientName']}
Blood Type Required: {request_data['blood']}
Hospital: {request_data['hospital']}
Location: {request_data.get('location', 'N/A')}

You have been matched as the nearest eligible donor.
Please respond as soon as possible.

Thank you for saving lives!

LifeLink Team"""
    
    send_email(donor_email, subject, body)
    return True

def process_blood_request_ai(db, request_id, request_data):
    """
    Main AI Agent workflow:
    1. User creates blood request
    2. AI Agent activates
    3. Filters donors (blood group)
    4. Checks cooldown eligibility
    5. Calculates distance (Haversine)
    6. Ranks nearest valid donors
    7. Notifies top donor
    """
    blood_type = request_data["blood"]
    request_lat = request_data.get("latitude", 0)
    request_lon = request_data.get("longitude", 0)
    
    # Match and rank donors
    eligible_donors = match_donors(db, blood_type, request_lat, request_lon)
    
    if not eligible_donors:
        return {
            "status": "error",
            "message": "No eligible donors found",
            "donors_checked": 0
        }
    
    # Notify top donor
    top_donor = eligible_donors[0]
    notify_donor(db, top_donor["id"], request_id, request_data, top_donor["email"])
    
    return {
        "status": "success",
        "message": f"Matched with {top_donor['name']} ({top_donor['distance']} km away)",
        "matched_donor": top_donor,
        "backup_donors": len(eligible_donors) - 1,
        "all_donors": eligible_donors[:5]  # Top 5 for backup
    }

def retry_next_donor(db, request_id, declined_donor_id):
    """
    If donor declines, try next donor in the list
    """
    # Get request details
    request_ref = db.collection("requests").document(request_id)
    request_doc = request_ref.get()
    
    if not request_doc.exists:
        return {"status": "error", "message": "Request not found"}
    
    request_data = request_doc.to_dict()
    
    # Get all eligible donors again
    eligible_donors = match_donors(
        db, 
        request_data["blood"], 
        request_data.get("latitude", 0), 
        request_data.get("longitude", 0)
    )
    
    # Filter out declined donor
    remaining_donors = [d for d in eligible_donors if d["id"] != declined_donor_id]
    
    if not remaining_donors:
        return {"status": "error", "message": "No more donors available"}
    
    # Notify next donor
    next_donor = remaining_donors[0]
    notify_donor(db, next_donor["id"], request_id, request_data, next_donor["email"])
    
    return {
        "status": "success",
        "message": f"Notified next donor: {next_donor['name']}",
        "donor": next_donor
    }
