#!/usr/bin/env python3
"""
eBird Public Page Scraper for NYC Rare Bird Alerts
Scrapes ONLY from the public eBird website - NO API
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from fetch_wikipedia import fetch_bird_info
import time
import re

# eBird alert URL for NYC
EBIRD_ALERT_URL = "https://ebird.org/alert/summary?sid=SN35466"

def scrape_ebird_alerts():
    """
    Scrape bird sightings from eBird public alert page.
    Returns list of raw sightings.
    """
    print(f"Scraping data from {EBIRD_ALERT_URL}...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }

    session = requests.Session()

    try:
        # First request to get any cookies
        print("Making initial request...")
        response = session.get(EBIRD_ALERT_URL, headers=headers, timeout=30, allow_redirects=True)

        print(f"Status code: {response.status_code}")
        print(f"Final URL: {response.url}")

        # Save the HTML for debugging
        with open('/tmp/ebird_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Saved page to /tmp/ebird_page.html for inspection")

        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for observations using the exact structure you provided
        obs_elements = soup.find_all('div', class_='Observation')

        if not obs_elements:
            print(f"\nERROR: Could not find any observation elements!")
            print(f"Page title: {soup.title.string if soup.title else 'No title'}")
            print(f"Looking for alternative structures...")

            # Try to find ANY div that might contain observations
            all_divs = soup.find_all('div')
            print(f"Total divs found: {len(all_divs)}")

            # Look for common eBird class names
            for class_name in ['observation', 'sighting', 'result', 'checklist']:
                elements = soup.find_all(class_=re.compile(class_name, re.I))
                if elements:
                    print(f"Found {len(elements)} elements with class containing '{class_name}'")

            print("\nThe page might require login. Check /tmp/ebird_page.html")
            return []

        print(f"\n✓ Found {len(obs_elements)} observations!")

        sightings = []

        for i, obs in enumerate(obs_elements, 1):
            try:
                # Extract bird species name - EXACT structure from your HTML
                species_elem = obs.find('span', class_='Heading-main')
                species = species_elem.get_text(strip=True) if species_elem else None

                # Extract scientific name
                sci_elem = obs.find('span', class_='Heading-sub--sci')
                scientific_name = sci_elem.get_text(strip=True) if sci_elem else ''

                # Extract date and time - look for checklist link
                date_elem = obs.find('a', href=lambda x: x and '/checklist/' in x)
                date_str = date_elem.get_text(strip=True) if date_elem else None

                # Extract location - look for Google Maps link
                location_elem = obs.find('a', href=lambda x: x and 'google.com/maps' in x)
                location = None
                lat = None
                lng = None

                if location_elem:
                    location = location_elem.get_text(strip=True)
                    # Extract coordinates from href
                    href = location_elem.get('href', '')
                    coords_match = re.search(r'query=([-\d.]+),([-\d.]+)', href)
                    if coords_match:
                        lat = float(coords_match.group(1))
                        lng = float(coords_match.group(2))

                # Extract observer name - EXACT structure from your HTML
                observer = "Anonymous"

                # Look for the GridFlex structure
                grid_cells = obs.find_all('div', class_='GridFlex-cell')
                for cell in grid_cells:
                    # Find the user icon
                    user_icon = cell.find('svg', class_='Icon--user')
                    if user_icon:
                        # Get the next cell which should contain the observer name
                        next_div = cell.find_next_sibling('div', class_='GridFlex-cell')
                        if next_div:
                            # Get all spans in this div
                            spans = next_div.find_all('span')
                            for span in spans:
                                # Skip the "Observer: " label
                                if 'is-visuallyHidden' not in span.get('class', []):
                                    observer_text = span.get_text(strip=True)
                                    if observer_text and observer_text != 'Observer:':
                                        observer = observer_text
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
                    print(f"  {i}. {species} - {observer} at {location}")
                else:
                    missing = []
                    if not species: missing.append("species")
                    if not location: missing.append("location")
                    if not lat or not lng: missing.append("coordinates")
                    print(f"  {i}. Skipped (missing: {', '.join(missing)})")

            except Exception as e:
                print(f"  {i}. Error: {e}")
                continue

        print(f"\n{'='*50}")
        print(f"Successfully extracted {len(sightings)} sightings!")
        print(f"{'='*50}\n")

        return sightings

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return []

def process_sighting(sighting):
    """
    Process a single sighting and enrich with Wikipedia data.
    """
    try:
        species = sighting.get('species', 'Unknown')
        scientific_name = sighting.get('scientific_name', '')
        location_name = sighting.get('location', 'Unknown location')
        date_str = sighting.get('date', '')
        observer = sighting.get('observer', 'Anonymous')
        lat = sighting.get('lat')
        lng = sighting.get('lng')

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
            'id': f"{species}_{location_name}_{date_str}".replace(' ', '_').replace(',', '').replace(':', '').replace('-', ''),
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

    print(f"\n✓ Saved {len(sightings)} sightings to {output_file}")

def main():
    """
    Main scraper function - ONLY scrapes website, NO API
    """
    print("="*60)
    print("eBird Web Scraper - NEW YORK RARE BIRDS")
    print("="*60)

    # Scrape the alert page
    raw_sightings = scrape_ebird_alerts()

    if not raw_sightings:
        print("\n❌ No sightings found or scraping failed.")
        print("Check the page HTML at /tmp/ebird_page.html")
        return

    print(f"\nProcessing {len(raw_sightings)} sightings...")
    print("-"*60)

    processed_sightings = []

    for raw in raw_sightings:
        processed = process_sighting(raw)
        if processed:
            processed_sightings.append(processed)

        time.sleep(0.3)  # Be nice to Wikipedia

    print("\n" + "="*60)
    print(f"✓ COMPLETE: {len(processed_sightings)} sightings saved!")
    print("="*60)

    # Save to JSON
    save_birds_data(processed_sightings)

if __name__ == "__main__":
    main()
