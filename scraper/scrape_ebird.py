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
import re

# eBird alert URL for NYC
EBIRD_ALERT_URL = "https://ebird.org/alert/summary?sid=SN35466"

def scrape_ebird_alerts():
    """
    Scrape bird sightings from eBird public alert page.
    Returns list of raw sightings.
    """
    print(f"Fetching data from {EBIRD_ALERT_URL}...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    try:
        session = requests.Session()
        response = session.get(EBIRD_ALERT_URL, headers=headers, timeout=15, allow_redirects=True)

        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print("The page may require authentication.")
            print("Falling back to eBird API...")
            return scrape_with_api_fallback()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for observations using the structure you provided
        obs_elements = soup.find_all('div', class_='Observation')

        if not obs_elements:
            print("Could not find observation elements on page.")
            print("Page may require login or structure has changed.")
            print("Falling back to eBird API...")
            return scrape_with_api_fallback()

        print(f"Found {len(obs_elements)} observations on page")

        sightings = []

        for obs in obs_elements:
            try:
                # Extract bird species name
                species_elem = obs.find('span', class_='Heading-main')
                species = species_elem.get_text(strip=True) if species_elem else None

                # Extract scientific name
                sci_elem = obs.find('span', class_='Heading-sub--sci')
                scientific_name = sci_elem.get_text(strip=True) if sci_elem else ''

                # Extract date and time
                date_elem = obs.find('a', href=lambda x: x and '/checklist/' in x)
                date_str = date_elem.get_text(strip=True) if date_elem else None

                # Extract location - look for Google Maps link
                location_elem = obs.find('a', href=lambda x: x and 'google.com/maps' in x)
                location = None
                lat = None
                lng = None

                if location_elem:
                    location = location_elem.get_text(strip=True)
                    # Extract coordinates from the href
                    href = location_elem.get('href', '')
                    coords_match = re.search(r'query=([-\d.]+),([-\d.]+)', href)
                    if coords_match:
                        lat = float(coords_match.group(1))
                        lng = float(coords_match.group(2))

                # Extract observer name - look for the specific structure
                observer = "Anonymous"
                # Find the observer section
                meta_divs = obs.find_all('div', class_='GridFlex-cell')
                for div in meta_divs:
                    # Look for the observer icon
                    icon = div.find('svg', class_='Icon--user')
                    if icon:
                        # The observer name should be in a span in the same parent
                        parent = div.parent
                        if parent:
                            observer_spans = parent.find_all('span')
                            for span in observer_spans:
                                text = span.get_text(strip=True)
                                if text and text != 'Observer:' and not span.get('class') or 'is-visuallyHidden' not in span.get('class', []):
                                    observer = text
                                    break

                if species and location and lat and lng:
                    sightings.append({
                        'species': species,
                        'scientific_name': scientific_name,
                        'location': location,
                        'lat': lat,
                        'lng': lng,
                        'date': date_str,
                        'observer': observer
                    })
                    print(f"  ✓ {species} by {observer} at {location}")

            except Exception as e:
                print(f"Error parsing observation: {e}")
                continue

        if not sightings:
            print("No valid sightings extracted, falling back to API...")
            return scrape_with_api_fallback()

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

    # New York State region code (to get all sightings from the state)
    region = 'US-NY'

    all_sightings = []
    base_url = "https://api.ebird.org/v2/data/obs"
    headers = {'X-eBirdApiToken': api_key}

    try:
        url = f"{base_url}/{region}/recent/notable"
        params = {'back': 7, 'detail': 'full', 'maxResults': 200}
        response = requests.get(url, params=params, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} notable sightings in {region}")

            for obs in data:
                all_sightings.append({
                    'species': obs.get('comName', 'Unknown'),
                    'scientific_name': obs.get('sciName', ''),
                    'location': obs.get('locName', 'Unknown'),
                    'date': obs.get('obsDt', ''),
                    'observer': obs.get('userDisplayName', 'Anonymous'),
                    'lat': obs.get('lat'),
                    'lng': obs.get('lng')
                })

        else:
            print(f"API error: {response.status_code}")

    except Exception as e:
        print(f"Error fetching from API: {e}")

    return all_sightings

def process_sighting(sighting):
    """
    Process a single sighting and enrich with location data.
    """
    try:
        species = sighting.get('species', 'Unknown')
        scientific_name = sighting.get('scientific_name', '')
        location_name = sighting.get('location', 'Unknown location')
        date_str = sighting.get('date', '')
        observer = sighting.get('observer', 'Anonymous')

        # Get coordinates
        lat = sighting.get('lat')
        lng = sighting.get('lng')

        if not lat or not lng:
            print(f"Geocoding location: {location_name}")
            coords = geocode_address(f"{location_name}, NY")
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
                'summary': f'{species} observed in New York.',
                'image_url': 'assets/images/placeholder-bird.svg',
                'source': ''
            }

        # Format the sighting
        formatted = {
            'id': f"{species}_{location_name}_{date_str}".replace(' ', '_').replace(',', '').replace(':', ''),
            'species': species,
            'scientific_name': scientific_name,
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
    print("Starting eBird scraper for New York rare birds...")
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
