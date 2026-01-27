#!/usr/bin/env python3
"""
eBird Public Page Scraper for NYC Rare Bird Alerts
Scrapes publicly available data from eBird alert pages.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from fetch_wikipedia import fetch_bird_info
from geocode import geocode_address
import time

# eBird alert URL for NYC
EBIRD_ALERT_URL = "https://ebird.org/alert/summary?sid=SN35466"

def scrape_ebird_alerts():
    """
    Scrape bird sightings from eBird public alert page.
    Returns list of raw sightings.
    """
    print(f"Fetching data from {EBIRD_ALERT_URL}...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        session = requests.Session()
        response = session.get(EBIRD_ALERT_URL, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print("The page may require authentication.")
            print("Falling back to eBird API...")
            return scrape_with_api_fallback()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to find sightings in common eBird HTML structures
        sightings = []

        # Look for observation cards or rows
        obs_elements = soup.find_all(['div', 'tr'], class_=lambda x: x and ('observation' in x.lower() or 'sighting' in x.lower() or 'result' in x.lower()))

        if not obs_elements:
            # Try alternative selectors
            obs_elements = soup.find_all('div', class_='Observation')

        if not obs_elements:
            print("Could not find observation elements on page.")
            print("Page may require login or structure has changed.")
            print("Falling back to eBird API...")
            return scrape_with_api_fallback()

        print(f"Found {len(obs_elements)} potential observation elements")

        for elem in obs_elements:
            try:
                # Extract bird name
                species_elem = elem.find(['a', 'span'], class_=lambda x: x and 'species' in x.lower())
                if not species_elem:
                    species_elem = elem.find('a', href=lambda x: x and '/species/' in x)

                species = species_elem.get_text(strip=True) if species_elem else None

                # Extract location
                loc_elem = elem.find(['a', 'span'], class_=lambda x: x and 'location' in x.lower())
                if not loc_elem:
                    loc_elem = elem.find('a', href=lambda x: x and '/hotspot/' in x)

                location = loc_elem.get_text(strip=True) if loc_elem else None

                # Extract date/time
                date_elem = elem.find(['time', 'span'], class_=lambda x: x and ('date' in x.lower() or 'time' in x.lower()))
                date_str = date_elem.get_text(strip=True) if date_elem else None

                # Extract observer
                observer_elem = elem.find(['a', 'span'], class_=lambda x: x and 'observer' in x.lower())
                if not observer_elem:
                    observer_elem = elem.find('a', href=lambda x: x and '/profile/' in x)

                observer = observer_elem.get_text(strip=True) if observer_elem else "Anonymous"

                if species and location:
                    sightings.append({
                        'species': species,
                        'location': location,
                        'date': date_str,
                        'observer': observer
                    })

            except Exception as e:
                print(f"Error parsing observation: {e}")
                continue

        return sightings

    except Exception as e:
        print(f"Error fetching page: {e}")
        print("Falling back to eBird API...")
        return scrape_with_api_fallback()

def scrape_with_api_fallback():
    """
    Fallback to eBird API if web scraping fails.
    """
    api_key = os.environ.get('EBIRD_API_KEY', '')

    if not api_key:
        print("ERROR: Cannot scrape page (requires login) and no EBIRD_API_KEY provided")
        print("Please either:")
        print("1. Get an eBird API key from https://ebird.org/api/keygen")
        print("2. Set EBIRD_API_KEY environment variable")
        return []

    print(f"Using eBird API with key: {api_key[:8]}...")

    # NYC region codes
    regions = ['US-NY-061', 'US-NY-047', 'US-NY-081', 'US-NY-005', 'US-NY-085']

    all_sightings = []
    base_url = "https://api.ebird.org/v2/data/obs"
    headers = {'X-eBirdApiToken': api_key}

    for region in regions:
        try:
            url = f"{base_url}/{region}/recent/notable"
            params = {'back': 7, 'detail': 'full'}
            response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                print(f"Found {len(data)} sightings in {region}")

                for obs in data:
                    all_sightings.append({
                        'species': obs.get('comName', 'Unknown'),
                        'location': obs.get('locName', 'Unknown'),
                        'date': obs.get('obsDt', ''),
                        'observer': obs.get('userDisplayName', 'Anonymous'),
                        'lat': obs.get('lat'),
                        'lng': obs.get('lng')
                    })

        except Exception as e:
            print(f"Error fetching from API for {region}: {e}")

    return all_sightings

def process_sighting(sighting):
    """
    Process a single sighting and enrich with location data.
    """
    try:
        species = sighting.get('species', 'Unknown')
        location_name = sighting.get('location', 'Unknown location')
        date_str = sighting.get('date', '')
        observer = sighting.get('observer', 'Anonymous')

        # Get coordinates
        lat = sighting.get('lat')
        lng = sighting.get('lng')

        if not lat or not lng:
            print(f"Geocoding location: {location_name}")
            coords = geocode_address(f"{location_name}, NYC, NY")
            if coords:
                lat = coords['lat']
                lng = coords['lng']
            else:
                print(f"Warning: Could not geocode {location_name}, skipping")
                return None

        # Fetch Wikipedia info for bird image
        print(f"Fetching Wikipedia info for {species}...")
        wikipedia_info = fetch_bird_info(species)

        if not wikipedia_info:
            wikipedia_info = {
                'summary': f'{species} observed in NYC area.',
                'image_url': 'assets/images/placeholder-bird.svg',
                'source': ''
            }

        # Format the sighting
        formatted = {
            'id': f"{species}_{location_name}_{date_str}".replace(' ', '_').replace(',', ''),
            'species': species,
            'location': {
                'name': location_name,
                'lat': float(lat),
                'lng': float(lng)
            },
            'date': date_str,
            'observer': observer,
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
    print("Starting eBird scraper for NYC rare birds...")
    print("=" * 50)

    # Scrape the alert page
    raw_sightings = scrape_ebird_alerts()

    if not raw_sightings:
        print("No sightings found.")
        return

    print(f"\nFound {len(raw_sightings)} raw sightings")
    print("Processing sightings...")

    processed_sightings = []

    for raw in raw_sightings:
        processed = process_sighting(raw)
        if processed:
            # Avoid duplicates
            if not any(s['id'] == processed['id'] for s in processed_sightings):
                processed_sightings.append(processed)

        time.sleep(0.5)  # Be nice to APIs

    print(f"\n=== Total unique sightings: {len(processed_sightings)} ===")

    # Save to JSON
    save_birds_data(processed_sightings)

    print("\nScraping complete!")

if __name__ == "__main__":
    main()
