#!/bin/bash

# Test script for the eBird scraper
# Usage: ./test_scraper.sh

echo "=========================================="
echo "NYC Rare Birds Scraper - Test Script"
echo "=========================================="
echo ""

# Check if EBIRD_API_KEY is set
if [ -z "$EBIRD_API_KEY" ]; then
    echo "ERROR: EBIRD_API_KEY environment variable is not set!"
    echo ""
    echo "Please set it using:"
    echo "  export EBIRD_API_KEY='your-api-key-here'"
    echo ""
    echo "Get your API key from: https://ebird.org/api/keygen"
    exit 1
fi

echo "API Key detected: ${EBIRD_API_KEY:0:8}..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    exit 1
fi

echo "Python version: $(python3 --version)"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Dependencies already installed"
fi
echo ""

# Run the scraper
echo "Running scraper..."
echo "=========================================="
python3 scrape_ebird.py
echo "=========================================="
echo ""

# Check if data file was created
if [ -f "../data/birds.json" ]; then
    echo "SUCCESS: data/birds.json created!"
    echo ""
    echo "Number of sightings: $(python3 -c "import json; data=json.load(open('../data/birds.json')); print(len(data['sightings']))")"
    echo ""
    echo "Preview of first sighting:"
    python3 -c "import json; data=json.load(open('../data/birds.json')); print(json.dumps(data['sightings'][0] if data['sightings'] else {}, indent=2))"
else
    echo "ERROR: data/birds.json was not created!"
    exit 1
fi

echo ""
echo "Test complete! You can now open index.html in a browser."
echo "Run a local server with: python3 -m http.server 8000"
