from datetime import datetime, timedelta
from database import get_db
from utils.haversine import calculate_distance
import json

class SimpleAgentOrchestrator:
    """Streamlined agent following exact workflow: Filter → Cooldown → Distance → Rank → Notify → Retry"""
    
    def process_blood_request(self, request_id, request_data):
        """
        Autonomous workflow:
        1. User creates blood request
        2. AI Agent activates
        3. Filters donors (blood group)
        4. Checks cooldown eligibility
        5. Calculates distance (Haversine)
        6. Ranks nearest valid donors
        7. Notifies top donor
        8. If declined → tries next
        """
        
        blood_type = request_data['blood']
        req_lat = request_data.get('latitude', 0)
        req_lon = request_data.get('longitude', 0)
        
        print(f"\n🤖 AI Agent Activated for Request #{request_id}")
        print(f"   Blood Type Needed: {blood_type}")
        
        # Step 1: Filter donors by blood group
        filtered_donors = self._filter_by_blood_group(blood_type)
        print(f"   ✓ Filtered {len(filtered_donors)} donors with {blood_type}")
        
        if not filtered_donors:
            return {
                'status': 'failed',
                'message': 'No donors found with matching blood type',
                'step': 'filter'
            }
        
        # Step 2: Check cooldown eligibility
        eligible_donors = self._check_cooldown_eligibility(filtered_donors)
        print(f"   ✓ {len(eligible_donors)} donors eligible (90-day cooldown passed)")
        
        if not eligible_donors:
            return {
                'status': 'failed',
                'message': 'No eligible donors (all in cooldown period)',
                'step': 'cooldown'
            }
        
        # Step 3: Calculate distance using Haversine
        donors_with_distance = self._calculate_distances(eligible_donors, req_lat, req_lon)
        print(f"   ✓ Calculated distances for all donors")
        
        # Step 4: Rank nearest valid donors
        ranked_donors = self._rank_by_distance(donors_with_distance)
        print(f"   ✓ Ranked donors by proximity")
        
        # Step 5: Notify top donor
        top_donor = ranked_donors[0]
        notification_id = self._notify_donor(top_donor, request_id, request_data)
        print(f"   ✓ Notified top donor: {top_donor['name']} ({top_donor['distance']} km away)")
        
        # Store ranked list for auto-retry
        self._store_ranked_donors(request_id, ranked_donors)
        
        return {
            'status': 'success',
            'donor': {
                'id': top_donor['id'],
                'name': top_donor['name'],
                'phone': top_donor['phone'],
                'distance': top_donor['distance']
            },
            'notification_id': notification_id,
            'backup_donors_count': len(ranked_donors) - 1,
            'workflow_complete': True
        }
    
    def _filter_by_blood_group(self, blood_type):
        """Step 1: Filter donors by blood group"""
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE blood=%s", (blood_type,))
        donors = cursor.fetchall()
        cursor.close()
        conn.close()
        return donors
    
    def _check_cooldown_eligibility(self, donors):
        """Step 2: Check 90-day cooldown eligibility"""
        eligible = []
        for donor in donors:
            if not donor['lastDonation']:
                eligible.append(donor)
            else:
                days_since = (datetime.now().date() - donor['lastDonation']).days
                if days_since >= 90:
                    eligible.append(donor)
        return eligible
    
    def _calculate_distances(self, donors, req_lat, req_lon):
        """Step 3: Calculate distance using Haversine formula"""
        donors_with_distance = []
        for donor in donors:
            distance = calculate_distance(
                req_lat, req_lon,
                float(donor['latitude']),
                float(donor['longitude'])
            )
            donor['distance'] = round(distance, 2)
            donors_with_distance.append(donor)
        return donors_with_distance
    
    def _rank_by_distance(self, donors):
        """Step 4: Rank nearest valid donors"""
        return sorted(donors, key=lambda x: x['distance'])
    
    def _notify_donor(self, donor, request_id, request_data):
        """Step 5: Notify top donor"""
        conn = get_db()
        cursor = conn.cursor()
        
        message = f"Blood donation needed for {request_data.get('patientName', 'a patient')} at {request_data.get('hospital', 'hospital')}. You are {donor['distance']} km away."
        
        cursor.execute("""
            INSERT INTO notifications (donor_id, request_id, message, status)
            VALUES (%s, %s, %s, 'sent')
        """, (donor['id'], request_id, message))
        
        conn.commit()
        notification_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return notification_id
    
    def _store_ranked_donors(self, request_id, ranked_donors):
        """Store ranked donor list for auto-retry"""
        conn = get_db()
        cursor = conn.cursor()
        
        donor_ids = json.dumps([d['id'] for d in ranked_donors])
        
        cursor.execute("""
            UPDATE requests 
            SET agent_analysis=%s 
            WHERE id=%s
        """, (donor_ids, request_id))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def handle_donor_response(self, notification_id, response):
        """
        Step 6: If declined → tries next
        Autonomous retry when donor declines
        """
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Update notification status
        cursor.execute("""
            UPDATE notifications 
            SET status=%s, response_time=TIMESTAMPDIFF(SECOND, created_at, NOW())
            WHERE id=%s
        """, (response, notification_id))
        
        # Get request info
        cursor.execute("""
            SELECT n.request_id, n.donor_id, r.blood, r.patientName, r.hospital, 
                   r.latitude, r.longitude, r.agent_analysis
            FROM notifications n
            JOIN requests r ON n.request_id = r.id
            WHERE n.id=%s
        """, (notification_id,))
        
        data = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if response == 'declined' and data:
            print(f"\n🔄 Donor declined. AI Agent auto-retrying...")
            return self._try_next_donor(data)
        
        return {'status': 'accepted', 'message': 'Donor accepted the request'}
    
    def _try_next_donor(self, data):
        """Step 6: Autonomous retry with next ranked donor"""
        request_id = data['request_id']
        declined_donor_id = data['donor_id']
        
        # Get ranked donor list
        ranked_donor_ids = json.loads(data['agent_analysis']) if data['agent_analysis'] else []
        
        # Get already contacted donors
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT donor_id FROM notifications WHERE request_id=%s
        """, (request_id,))
        contacted = [row['donor_id'] for row in cursor.fetchall()]
        
        # Find next donor
        next_donor_id = None
        for donor_id in ranked_donor_ids:
            if donor_id not in contacted:
                next_donor_id = donor_id
                break
        
        if not next_donor_id:
            cursor.close()
            conn.close()
            return {
                'status': 'exhausted',
                'message': 'All ranked donors have been contacted'
            }
        
        # Get next donor details
        cursor.execute("SELECT * FROM users WHERE id=%s", (next_donor_id,))
        next_donor = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Calculate distance for next donor
        next_donor['distance'] = round(calculate_distance(
            float(data['latitude']), float(data['longitude']),
            float(next_donor['latitude']), float(next_donor['longitude'])
        ), 2)
        
        # Notify next donor
        request_data = {
            'patientName': data['patientName'],
            'hospital': data['hospital']
        }
        notification_id = self._notify_donor(next_donor, request_id, request_data)
        
        print(f"   ✓ Contacted next donor: {next_donor['name']} ({next_donor['distance']} km away)")
        
        return {
            'status': 'retry_sent',
            'donor': {
                'name': next_donor['name'],
                'phone': next_donor['phone'],
                'distance': next_donor['distance']
            },
            'notification_id': notification_id,
            'attempt': len(contacted) + 1
        }
