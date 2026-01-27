import requests
import re
import os
from urllib.parse import unquote
import time

def fetch_bird_info(species_name):
    """
    Fetch bird information and image from Wikipedia.
    Returns dict with summary and image_url, or None if not found.
    """
    try:
        # Clean up species name for Wikipedia search
        search_name = species_name.strip().replace(' ', '_')

        print(f"  Searching Wikipedia for: {search_name}")

        # Try Wikipedia REST API v1
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_name}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

        response = requests.get(api_url, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()

            # Extract summary - focus on first 2-3 sentences
            summary = data.get('extract', '')
            if summary:
                sentences = re.split(r'(?<=[.!?])\s+', summary)
                summary = ' '.join(sentences[:3]) if len(sentences) >= 3 else summary

            # Get image URL - prefer original over thumbnail
            image_url = data.get('originalimage', {}).get('source', '')
            if not image_url:
                image_url = data.get('thumbnail', {}).get('source', '')

            # Download and cache image locally
            local_image_path = None
            if image_url:
                local_image_path = download_image(image_url, species_name)
                if local_image_path:
                    print(f"  ✓ Got image: {local_image_path}")
                else:
                    print(f"  ⚠ Could not download image, using placeholder")
                    local_image_path = 'assets/images/placeholder-bird.svg'
            else:
                print(f"  ⚠ No image found on Wikipedia")
                local_image_path = 'assets/images/placeholder-bird.svg'

            return {
                'summary': summary,
                'image_url': local_image_path,
                'source': data.get('content_urls', {}).get('desktop', {}).get('page', '')
            }
        else:
            print(f"  ⚠ Wikipedia returned {response.status_code}, using placeholder")
            return {
                'summary': f'{species_name} is a bird species observed in New York.',
                'image_url': 'assets/images/placeholder-bird.svg',
                'source': ''
            }

    except Exception as e:
        print(f"  ⚠ Error fetching Wikipedia: {e}")
        return {
            'summary': f'{species_name} is a bird species.',
            'image_url': 'assets/images/placeholder-bird.svg',
            'source': ''
        }

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
        ext = image_url.split('.')[-1].split('?')[0].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp']:
            ext = 'jpg'

        filename = f"{safe_name}.{ext}"

        # Determine cache directory path
        cache_dir = os.path.join('..', 'assets', 'cache', 'wikipedia-images')
        if not os.path.exists(cache_dir):
            cache_dir = os.path.join('assets', 'cache', 'wikipedia-images')

        os.makedirs(cache_dir, exist_ok=True)

        filepath = os.path.join(cache_dir, filename)

        # Check if already cached
        if os.path.exists(filepath):
            return f"assets/cache/wikipedia-images/{filename}"

        # Download image with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Referer': 'https://en.wikipedia.org/',
        }

        response = requests.get(image_url, headers=headers, timeout=20, stream=True)

        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Verify file was written
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                return f"assets/cache/wikipedia-images/{filename}"
            else:
                print(f"    Downloaded file is empty")
                return None
        else:
            print(f"    Download failed with status {response.status_code}")
            return None

    except Exception as e:
        print(f"    Error downloading: {e}")
        return None

if __name__ == "__main__":
    # Test the function
    test_species = ["Snow Goose", "Bald Eagle", "Blue-winged Teal"]

    for species in test_species:
        print(f"\n{'='*60}")
        print(f"Testing: {species}")
        print('='*60)
        result = fetch_bird_info(species)
        if result:
            print(f"Summary: {result['summary'][:100]}...")
            print(f"Image: {result['image_url']}")
        time.sleep(1)
