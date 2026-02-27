from datetime import datetime, timedelta
from database import get_db
from utils.haversine import calculate_distance
try:
    from services.email_service import send_email
    EMAIL_ENABLED = True
except:
    EMAIL_ENABLED = False

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

def notify_donor(donor_id, request_id, donor_email, donor_phone, patient_name, hospital):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notifications (donor_id, request_id, status) VALUES (%s, %s, 'sent')", (donor_id, request_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    subject = "🚨 URGENT: Blood Donation Request"
    message = f"""Dear Donor,

🚨 URGENT BLOOD DONATION REQUEST

Patient: {patient_name}
Hospital: {hospital}
You are the nearest eligible donor!

Please respond immediately if you can donate.

Thank you,
LifeLink Team"""
    
    if EMAIL_ENABLED:
        send_email(donor_email, subject, message)
    else:
        print(f"\n📧 EMAIL NOTIFICATION (Simulated)")
        print(f"To: {donor_email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}\n")

def process_blood_request(request_id, blood_type, latitude, longitude, patient_name, hospital):
    ranked_donors = find_best_donors(blood_type, latitude, longitude)
    
    if not ranked_donors:
        return {"status": "failed", "message": "No eligible donors found"}
    
    for donor in ranked_donors:
        notify_donor(donor['id'], request_id, donor['email'], donor['phone'], patient_name, hospital)
        return {
            "status": "success",
            "donor": {
                "name": donor['name'],
                "email": donor['email'],
                "distance": round(donor['distance'], 2)
            }
        }
    
    return {"status": "failed", "message": "No donors available"}
