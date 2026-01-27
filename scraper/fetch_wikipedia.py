import requests
import re
import os
from urllib.parse import unquote

def fetch_bird_info(species_name):
    """
    Fetch bird information and image from Wikipedia.
    Returns dict with summary and image_url, or None if not found.
    """
    try:
        # Clean up species name for Wikipedia search
        search_name = species_name.strip()

        # Try Wikipedia API
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_name}"
        response = requests.get(api_url, timeout=10)

        if response.status_code != 200:
            print(f"Wikipedia API returned {response.status_code} for {species_name}")
            return None

        data = response.json()

        # Extract summary - focus on first 2-3 sentences about physical characteristics
        summary = data.get('extract', '')
        if summary:
            # Get first 2-3 sentences
            sentences = re.split(r'(?<=[.!?])\s+', summary)
            summary = ' '.join(sentences[:3]) if len(sentences) >= 3 else summary

        # Get image
        image_url = data.get('thumbnail', {}).get('source', '')
        original_image = data.get('originalimage', {}).get('source', '')

        # Prefer original image for better quality
        image_url = original_image if original_image else image_url

        # Download and cache image locally
        local_image_path = None
        if image_url:
            local_image_path = download_image(image_url, species_name)

        return {
            'summary': summary,
            'image_url': local_image_path if local_image_path else 'assets/images/placeholder-bird.svg',
            'source': data.get('content_urls', {}).get('desktop', {}).get('page', '')
        }

    except Exception as e:
        print(f"Error fetching Wikipedia info for {species_name}: {e}")
        return None

def download_image(image_url, species_name):
    """
    Download image from Wikipedia and save to local cache.
    Returns local file path relative to project root.
    """
    try:
        # Create safe filename from species name
        safe_name = re.sub(r'[^\w\s-]', '', species_name.lower())
        safe_name = re.sub(r'[-\s]+', '-', safe_name)

        # Get file extension from URL
        ext = image_url.split('.')[-1].split('?')[0]
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'svg']:
            ext = 'jpg'

        filename = f"{safe_name}.{ext}"

        # Determine the correct path
        # When running from scraper directory
        cache_dir = os.path.join('..', 'assets', 'cache', 'wikipedia-images')
        # When running from GitHub Actions (root)
        if not os.path.exists(cache_dir):
            cache_dir = os.path.join('assets', 'cache', 'wikipedia-images')

        os.makedirs(cache_dir, exist_ok=True)

        filepath = os.path.join(cache_dir, filename)

        # Check if already cached
        if os.path.exists(filepath):
            # Return path relative to project root
            return f"assets/cache/wikipedia-images/{filename}"

        # Download image
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded image for {species_name}")
            return f"assets/cache/wikipedia-images/{filename}"
        else:
            print(f"Failed to download image for {species_name}: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error downloading image for {species_name}: {e}")
        return None

if __name__ == "__main__":
    # Test the function
    test_species = "Snowy Owl"
    result = fetch_bird_info(test_species)
    if result:
        print(f"Species: {test_species}")
        print(f"Summary: {result['summary'][:100]}...")
        print(f"Image: {result['image_url']}")
    else:
        print(f"Failed to fetch info for {test_species}")
