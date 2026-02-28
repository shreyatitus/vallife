import requests

def get_coordinates(location):
    """Convert location text to latitude/longitude using Nominatim (OpenStreetMap)"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "LifeLink Blood Donation App"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        
        if data and len(data) > 0:
            return {
                "latitude": float(data[0]["lat"]),
                "longitude": float(data[0]["lon"]),
                "display_name": data[0].get("display_name", location)
            }
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None
