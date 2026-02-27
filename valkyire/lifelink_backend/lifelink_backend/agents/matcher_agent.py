from datetime import datetime, timedelta
from database import get_db
from utils.haversine import calculate_distance
import json

class MatcherAgent:
    def __init__(self):
        self.learning_enabled = True
        
    def get_donor_patterns(self, donor_id):
        """Retrieve learned patterns about donor behavior"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM donor_patterns WHERE donor_id=%s", (donor_id,))
        pattern = cursor.fetchone()
        cursor.close()
        conn.close()
        return pattern
    
    def predict_donor_availability(self, donor):
        """Predict likelihood of donor responding positively"""
        pattern = self.get_donor_patterns(donor['id'])
        
        if not pattern:
            return 0.5  # Default probability
        
        # Calculate score based on historical data
        response_rate = pattern.get('response_rate', 0.5)
        avg_response_time = pattern.get('avg_response_time', 3600)
        
        # Time-based scoring
        current_hour = datetime.now().hour
        preferred_time = pattern.get('preferred_time', '9-17')
        
        time_score = 1.0
        if preferred_time:
            start, end = map(int, preferred_time.split('-'))
            if start <= current_hour <= end:
                time_score = 1.2
            else:
                time_score = 0.7
        
        availability_score = response_rate * time_score
        return min(availability_score, 1.0)
    
    def find_optimal_donors(self, blood_type, req_lat, req_lon, urgency="medium"):
        """Find and rank donors using multi-criteria optimization"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE blood=%s", (blood_type,))
        donors = cursor.fetchall()
        cursor.close()
        conn.close()
        
        scored_donors = []
        for donor in donors:
            # Check cooldown
            if donor['lastDonation']:
                days_since = (datetime.now().date() - donor['lastDonation']).days
                if days_since < 90:
                    continue
            
            # Calculate distance
            distance = calculate_distance(
                req_lat, req_lon, 
                float(donor['latitude']), 
                float(donor['longitude'])
            )
            
            # Predict availability
            availability = self.predict_donor_availability(donor)
            
            # Multi-criteria scoring
            distance_score = max(0, 1 - (distance / 50))  # Normalize to 50km
            history_score = min(donor['donations'] / 10, 1.0)  # Reward experience
            
            # Urgency-based weighting
            if urgency == "critical":
                weights = {"distance": 0.6, "availability": 0.3, "history": 0.1}
            elif urgency == "high":
                weights = {"distance": 0.5, "availability": 0.3, "history": 0.2}
            else:
                weights = {"distance": 0.4, "availability": 0.4, "history": 0.2}
            
            total_score = (
                distance_score * weights["distance"] +
                availability * weights["availability"] +
                history_score * weights["history"]
            )
            
            scored_donors.append({
                **donor,
                'distance': round(distance, 2),
                'availability_score': round(availability, 2),
                'total_score': round(total_score, 2)
            })
        
        return sorted(scored_donors, key=lambda x: x['total_score'], reverse=True)
    
    def update_donor_pattern(self, donor_id, response_time, accepted):
        """Learn from donor responses to improve future predictions"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM donor_patterns WHERE donor_id=%s", (donor_id,))
        pattern = cursor.fetchone()
        
        current_hour = datetime.now().hour
        time_slot = f"{max(9, current_hour-1)}-{min(21, current_hour+1)}"
        
        if pattern:
            # Update existing pattern
            new_response_rate = (pattern['response_rate'] * 0.8) + (0.2 if accepted else 0)
            new_avg_time = (pattern['avg_response_time'] * 0.7) + (response_time * 0.3)
            
            cursor.execute("""
                UPDATE donor_patterns 
                SET avg_response_time=%s, response_rate=%s, preferred_time=%s, last_updated=NOW()
                WHERE donor_id=%s
            """, (int(new_avg_time), new_response_rate, time_slot, donor_id))
        else:
            # Create new pattern
            cursor.execute("""
                INSERT INTO donor_patterns (donor_id, avg_response_time, response_rate, preferred_time)
                VALUES (%s, %s, %s, %s)
            """, (donor_id, response_time, 1.0 if accepted else 0.0, time_slot))
        
        conn.commit()
        cursor.close()
        conn.close()
