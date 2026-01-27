// Initialize map centered on NYC with restricted bounds to show only NY state
const map = L.map('map', {
    maxBounds: [[40.0, -75.0], [41.5, -73.0]], // Bounds for NYC area
    maxBoundsViscosity: 1.0
}).setView([40.7128, -74.0060], 10);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19
}).addTo(map);

// Custom icon for bird markers
const birdIcon = L.divIcon({
    className: 'bird-marker',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
    popupAnchor: [0, -10]
});

// Format date for display
function formatDate(dateString) {
    if (!dateString) return 'Unknown date';

    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return dateString;
    }
}

// Create popup content for a bird sighting with hover format including photo
function createHoverPopup(bird) {
    // Create Google Maps link for location
    const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${bird.location.lat},${bird.location.lng}`;

    // Get bird image - either from wikipedia cache or placeholder
    const birdImage = bird.wikipedia && bird.wikipedia.image_url ? bird.wikipedia.image_url : 'assets/images/placeholder-bird.svg';

    return `
        <div class="bird-hover-popup">
            <img src="${birdImage}" alt="${bird.species}" class="bird-photo" onerror="this.src='assets/images/placeholder-bird.svg'">
            <div class="bird-name">${bird.species}</div>
            <div class="sighting-info">
                <div class="info-row">
                    <strong>Last sighted by:</strong> ${bird.observer}
                </div>
                <div class="info-row">
                    <strong>Date and time:</strong> ${formatDate(bird.date)}
                </div>
                <div class="info-row">
                    <strong>Location:</strong> <a href="${mapsUrl}" target="_blank" class="location-link">${bird.location.name}</a>
                </div>
            </div>
        </div>
    `;
}

// Show loading indicator
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.id = 'loading';
    loadingDiv.innerHTML = `
        <div class="loading-spinner"></div>
        <p>Loading rare bird sightings...</p>
    `;
    document.body.appendChild(loadingDiv);
}

// Hide loading indicator
function hideLoading() {
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// Load and display bird data
async function loadBirdData() {
    showLoading();

    try {
        const response = await fetch('data/birds.json');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const sightings = data.sightings || [];

        console.log(`Loaded ${sightings.length} bird sightings`);

        if (sightings.length === 0) {
            hideLoading();
            alert('No bird sightings found. The data may not have been scraped yet.');
            return;
        }

        // Process each sighting
        sightings.forEach(bird => {
            // Create marker
            const marker = L.marker(
                [bird.location.lat, bird.location.lng],
                { icon: birdIcon }
            );

            // Create popup
            const popup = L.popup({
                closeButton: false,
                className: 'hover-popup'
            }).setContent(createHoverPopup(bird));

            // Bind popup to marker
            marker.bindPopup(popup);

            // Show popup on hover instead of click
            marker.on('mouseover', function() {
                this.openPopup();
            });

            marker.on('mouseout', function() {
                this.closePopup();
            });

            // Also allow click to keep popup open
            marker.on('click', function() {
                this.openPopup();
            });

            // Add marker to map
            marker.addTo(map);
        });

        // Update last updated time
        updateLastUpdated(data.last_updated);

        hideLoading();

    } catch (error) {
        console.error('Error loading bird data:', error);
        hideLoading();

        // Show error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'loading';
        errorDiv.innerHTML = `
            <p style="color: #e74c3c;">
                <strong>Error loading bird data</strong><br>
                ${error.message}<br><br>
                Please make sure the scraper has run at least once.
            </p>
        `;
        document.body.appendChild(errorDiv);
    }
}

// Update last updated time in footer
function updateLastUpdated(timestamp) {
    if (!timestamp) return;

    try {
        const date = new Date(timestamp);
        const formatted = date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZoneName: 'short'
        });

        const footer = document.querySelector('footer p');
        if (footer) {
            footer.innerHTML = `
                Data from <a href="https://ebird.org" target="_blank">eBird</a> |
                Last updated: ${formatted}
            `;
        }
    } catch (e) {
        console.error('Error formatting timestamp:', e);
    }
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadBirdData();
});
