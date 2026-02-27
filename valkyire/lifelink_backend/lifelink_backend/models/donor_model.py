from datetime import datetime

class Donor:
    def __init__(self, name, blood_type, latitude, longitude):
        self.name = name
        self.blood_type = blood_type
        self.latitude = latitude
        self.longitude = longitude
        self.last_donation = None
        self.points = 0

    def donate(self):
        self.last_donation = datetime.now()
        self.points += 10