// Initialize map centered on NYC
const map = L.map('map').setView([40.7128, -74.0060], 11);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19
}).addTo(map);

// Create marker cluster group
const markers = L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 50
});

// Store heat data
let heatData = [];

// Custom icon for bird markers
const birdIcon = L.divIcon({
    className: 'bird-marker',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
    popupAnchor: [0, -10]
});

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

// Create popup content for a bird sighting
function createPopupContent(bird) {
    return `
        <div class="bird-popup">
            <img src="${bird.wikipedia.image_url}"
                 alt="${bird.species}"
                 onerror="this.src='assets/images/placeholder-bird.svg'">
            <div class="bird-popup-content">
                <h3>${bird.species}</h3>
                <div class="scientific-name">${bird.scientific_name}</div>
                <p>${bird.wikipedia.summary || 'No description available.'}</p>
                <div class="metadata">
                    <div><strong>Location:</strong> ${bird.location.name}</div>
                    <div><strong>Date:</strong> ${formatDate(bird.date)}</div>
                    <div><strong>Observer:</strong> ${bird.observer}</div>
                    ${bird.count ? `<div><strong>Count:</strong> ${bird.count}</div>` : ''}
                </div>
            </div>
        </div>
    `;
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

            // Add popup
            marker.bindPopup(createPopupContent(bird), {
                maxWidth: 300,
                className: 'bird-popup-wrapper'
            });

            // Add to cluster group
            markers.addLayer(marker);

            // Add to heat map data
            heatData.push([bird.location.lat, bird.location.lng, 0.5]);
        });

        // Add markers to map
        map.addLayer(markers);

        // Add heat layer
        if (heatData.length > 0) {
            const heat = L.heatLayer(heatData, {
                radius: 25,
                blur: 35,
                maxZoom: 13,
                max: 1.0,
                gradient: {
                    0.0: '#3498db',
                    0.5: '#f39c12',
                    1.0: '#e74c3c'
                }
            }).addTo(map);
        }

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
