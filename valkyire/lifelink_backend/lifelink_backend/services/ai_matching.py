from datetime import datetime, timedelta
from database import get_db
from utils.haversine import calculate_distance

def check_cooldown(last_donation_date):
    if not last_donation_date:
        return True
    days_since = (datetime.now().date() - last_donation_date).days
    return days_since >= 90

def find_best_donors(blood_type, req_lat, req_lon):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE blood=%s", (blood_type,))
    donors = cursor.fetchall()
    cursor.close()
    conn.close()
    
    eligible = []
    for donor in donors:
        if check_cooldown(donor['lastDonation']):
            distance = calculate_distance(req_lat, req_lon, float(donor['latitude']), float(donor['longitude']))
            eligible.append({**donor, 'distance': distance})
    
    return sorted(eligible, key=lambda x: x['distance'])

def notify_donor(donor_id, request_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notifications (donor_id, request_id) VALUES (%s, %s)", (donor_id, request_id))
    conn.commit()
    cursor.close()
    conn.close()

def process_blood_request(request_id, blood_type, latitude, longitude):
    ranked_donors = find_best_donors(blood_type, latitude, longitude)
    
    if not ranked_donors:
        return {"status": "failed", "message": "No eligible donors found"}
    
    for donor in ranked_donors:
        notify_donor(donor['id'], request_id)
        return {
            "status": "success",
            "donor": {
                "name": donor['name'],
                "phone": donor['phone'],
                "distance": round(donor['distance'], 2)
            }
        }
    
    return {"status": "failed", "message": "No donors available"}
