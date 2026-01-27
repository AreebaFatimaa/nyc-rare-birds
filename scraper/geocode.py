import requests
import time

def geocode_address(address):
    """
    Geocode an address using Nominatim (OpenStreetMap).
    Returns dict with lat/lng or None if not found.
    Respects 1 request per second rate limit.
    """
    try:
        # Clean up address
        address = address.strip()

        # Nominatim API endpoint
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'bounded': 1,
            'viewbox': '-74.5,40.4,-73.5,41.0',  # NYC bounding box
        }
        headers = {
            'User-Agent': 'NYC-Rare-Birds-Map/1.0'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            results = response.json()
            if results and len(results) > 0:
                result = results[0]
                return {
                    'lat': float(result['lat']),
                    'lng': float(result['lon'])
                }

        print(f"Could not geocode address: {address}")
        return None

    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return None

    finally:
        # Respect rate limit: 1 request per second
        time.sleep(1)

if __name__ == "__main__":
    # Test the function
    test_address = "Central Park, Manhattan, NY"
    result = geocode_address(test_address)
    if result:
        print(f"Address: {test_address}")
        print(f"Coordinates: {result['lat']}, {result['lng']}")
    else:
        print(f"Failed to geocode {test_address}")
