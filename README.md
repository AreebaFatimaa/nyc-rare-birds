# Birds of NYC - Rare Bird Sightings Map

An automated, interactive map displaying rare bird sightings in New York City. Updated daily with data from eBird, featuring bird photos and descriptions from Wikipedia.

## Features

- **Interactive Map**: Explore rare bird sightings across all five NYC boroughs
- **Daily Updates**: Automatically refreshes at 4am EST via GitHub Actions
- **Rich Information**: Click any bird marker to see photos and descriptions
- **Clustering**: Markers group together at zoomed-out views for clarity
- **No API Keys Required**: (for viewing - deployment requires eBird API key)

## Live Demo

Visit the live site at: `https://areebafatimaa.github.io/nyc-rare-birds`

## How It Works

1. **Data Collection**: Python scraper fetches notable bird sightings from eBird API
3. **Storage**: Saves data to JSON file in the repository
4. **Visualization**: Leaflet.js displays sightings on an interactive map
5. **Automation**: GitHub Actions runs the scraper daily at 4am EST

## Setup Instructions

### Prerequisites

- GitHub account

### Deployment Steps

1. **Fork or Clone This Repository**
   ```bash
   git clone https://github.com/[your-username]/nyc-rare-birds.git
   cd nyc-rare-birds
   ```

2. **Enable GitHub Pages**
   - Go to Settings > Pages
   - Source: Deploy from a branch
   - Branch: `main` / `root`
   - Click Save

3. **Run the Scraper Manually (First Time)**
   - Go to Actions tab
   - Click "Update Bird Sightings" workflow
   - Click "Run workflow" > "Run workflow"
   - Wait for it to complete (~2-5 minutes)

4. **Visit Your Site**
   - Your site will be live at: `https://[your-username].github.io/nyc-rare-birds`
   - It may take a few minutes for GitHub Pages to deploy

## Local Development

### Test the Scraper Locally

```bash
# Install Python dependencies
cd scraper
pip install -r requirements.txt

# Set your eBird API key
export EBIRD_API_KEY="your-api-key-here"

# Run the scraper
python scrape_ebird.py

# Check the output
cat ../data/birds.json
```

### Test the Frontend Locally

```bash
# From the project root
python -m http.server 8000

# Open browser to http://localhost:8000
```

## Project Structure

```
nyc-rare-birds/
├── .github/
│   └── workflows/
│       └── update-birds.yml       # GitHub Actions workflow
├── scraper/
│   ├── scrape_ebird.py            # Main eBird scraper
│   ├── fetch_wikipedia.py         # Wikipedia API client
│   ├── geocode.py                 # Address geocoding
│   └── requirements.txt           # Python dependencies
├── data/
│   └── birds.json                 # Bird sightings data (auto-generated)
├── assets/
│   ├── images/
│   │   ├── bird-silhouette.svg    # Header icon
│   │   ├── binocular-man.svg      # Footer icon
│   │   └── placeholder-bird.svg   # Fallback image
│   └── cache/
│       └── wikipedia-images/      # Cached bird photos
├── index.html                      # Main page
├── map.js                          # Map logic
├── styles.css                      # Styling
└── README.md                       # This file
```

## Data Sources

- **Bird Sightings**: [eBird](https://ebird.org) - Cornell Lab of Ornithology
- **Bird Information**: [Wikipedia](https://wikipedia.org) - Free encyclopedia
- **Map Tiles**: [OpenStreetMap](https://openstreetmap.org) - Open map data

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Map Library**: [Leaflet.js](https://leafletjs.com)
- **Clustering**: Leaflet.markercluster
- **Backend**: Python 3.11
- **Automation**: GitHub Actions
- **Hosting**: GitHub Pages

## Customization

### Change Update Schedule

Edit `.github/workflows/update-birds.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # Change this cron expression
```

Cron format: `minute hour day month weekday` (in UTC)

### Change NYC Region Coverage

Edit `scraper/scrape_ebird.py`:

```python
NYC_REGIONS = [
    'US-NY-061',  # Manhattan
    'US-NY-047',  # Brooklyn
    'US-NY-081',  # Queens
    'US-NY-005',  # Bronx
    'US-NY-085',  # Staten Island
]
```

### Change Data Retention Period

Edit `scraper/scrape_ebird.py`:

```python
fetch_notable_sightings(region, days_back=7)  # Change from 7 to desired days
```

## Troubleshooting

### No bird sightings appearing on map

1. Check if `data/birds.json` exists and has data
2. Verify the GitHub Actions workflow ran successfully (Actions tab)
3. Check browser console for errors (F12)

### Scraper fails in GitHub Actions

1. Verify `EBIRD_API_KEY` is set correctly in GitHub Secrets
2. Check the Actions logs for error messages
3. Test the scraper locally with your API key

### Wikipedia images not loading

- Some birds may not have images on Wikipedia
- Fallback placeholder image will be shown
- Check `assets/cache/wikipedia-images/` directory

### Map not centering correctly

- Clear browser cache
- Check if latitude/longitude values in `data/birds.json` are valid

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Credits

- Data provided by [eBird](https://ebird.org)
- Bird information from [Wikipedia](https://wikipedia.org)
- Map tiles from [OpenStreetMap](https://openstreetmap.org)
- Built with [Leaflet.js](https://leafletjs.com)

---

**Note**: This project is for educational purposes. 
