#!/usr/bin/env python3
"""
eBird Rare Bird Scraper for NYC
Uses eBird API 2.0 to fetch notable bird sightings in NYC region.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Try to load .env file for local development
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment from {env_path}")
except ImportError:
    # python-dotenv not installed, use system environment
    pass

from fetch_wikipedia import fetch_bird_info
from geocode import geocode_address

# eBird API configuration
EBIRD_API_BASE = "https://api.ebird.org/v2"
EBIRD_API_KEY = os.environ.get('EBIRD_API_KEY', '')

# NYC region codes (can use multiple)
NYC_REGIONS = [
    'US-NY-061',  # New York County (Manhattan)
    'US-NY-047',  # Kings County (Brooklyn)
    'US-NY-081',  # Queens County
    'US-NY-005',  # Bronx County
    'US-NY-085',  # Richmond County (Staten Island)
]

# Alternative: use broader region
NYC_REGION_BROAD = 'US-NY'

def fetch_notable_sightings(region_code, days_back=7):
    """
    Fetch notable (rare) bird sightings from eBird API.
    Returns list of sightings.
    """
    url = f"{EBIRD_API_BASE}/data/obs/{region_code}/recent/notable"
    params = {
        'back': days_back,  # Days to look back
        'detail': 'full',   # Get full details
    }
    headers = {
        'X-eBirdApiToken': EBIRD_API_KEY
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"eBird API error for {region_code}: {response.status_code}")
            print(f"Response: {response.text}")
            return []

    except Exception as e:
        print(f"Error fetching sightings for {region_code}: {e}")
        return []

def process_sighting(sighting):
    """
    Process a single sighting and enrich with Wikipedia data.
    Returns formatted sighting dict.
    """
    try:
        species = sighting.get('comName', 'Unknown')
        scientific_name = sighting.get('sciName', '')

        # Extract location info
        location_name = sighting.get('locName', 'Unknown location')
        lat = sighting.get('lat')
        lng = sighting.get('lng')

        # If no coordinates, try to geocode the location name
        if not lat or not lng:
            coords = geocode_address(f"{location_name}, NYC, NY")
            if coords:
                lat = coords['lat']
                lng = coords['lng']
            else:
                print(f"Warning: No coordinates for {location_name}, skipping")
                return None

        # Fetch Wikipedia info
        print(f"Fetching Wikipedia info for {species}...")
        wikipedia_info = fetch_bird_info(species)

        if not wikipedia_info:
            # Use default if Wikipedia lookup fails
            wikipedia_info = {
                'summary': f'{species} observed in NYC area.',
                'image_url': 'assets/images/placeholder-bird.svg',
                'source': ''
            }

        # Format the sighting
        formatted = {
            'id': sighting.get('subId', '') + '_' + sighting.get('speciesCode', ''),
            'species': species,
            'scientific_name': scientific_name,
            'location': {
                'name': location_name,
                'lat': float(lat),
                'lng': float(lng)
            },
            'date': sighting.get('obsDt', ''),
            'observer': sighting.get('userDisplayName', 'Anonymous'),
            'count': sighting.get('howMany', 1),
            'wikipedia': wikipedia_info
        }

        return formatted

    except Exception as e:
        print(f"Error processing sighting: {e}")
        return None

def save_birds_data(sightings):
    """
    Save processed sightings to JSON file.
    """
    # Determine correct path (works both locally and in GitHub Actions)
    data_dir = os.path.join('..', 'data') if os.path.exists(os.path.join('..', 'data')) else 'data'
    os.makedirs(data_dir, exist_ok=True)

    output_file = os.path.join(data_dir, 'birds.json')

    data = {
        'last_updated': datetime.utcnow().isoformat() + 'Z',
        'sightings': sightings
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(sightings)} sightings to {output_file}")

def main():
    """
    Main scraper function.
    """
    if not EBIRD_API_KEY:
        print("ERROR: EBIRD_API_KEY environment variable not set!")
        print("Get your API key from: https://ebird.org/api/keygen")
        return

    print("Starting eBird scraper for NYC rare birds...")
    print(f"Using API key: {EBIRD_API_KEY[:8]}...")

    all_sightings = []

    # Fetch from all NYC regions
    for region in NYC_REGIONS:
        print(f"\nFetching notable sightings from {region}...")
        raw_sightings = fetch_notable_sightings(region, days_back=7)
        print(f"Found {len(raw_sightings)} notable sightings in {region}")

        # Process each sighting
        for raw_sighting in raw_sightings:
            processed = process_sighting(raw_sighting)
            if processed:
                # Avoid duplicates
                if not any(s['id'] == processed['id'] for s in all_sightings):
                    all_sightings.append(processed)

    print(f"\n=== Total unique sightings: {len(all_sightings)} ===")

    # Save to JSON
    save_birds_data(all_sightings)

    print("\nScraping complete!")

if __name__ == "__main__":
    main()
