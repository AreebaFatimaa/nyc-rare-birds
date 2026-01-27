# Quick Start Guide

Get your NYC Rare Birds Map up and running in 5 minutes!

## Step 1: Get Your eBird API Key

1. Visit https://ebird.org/api/keygen
2. Create an account or log in
3. Request an API key (instant approval)
4. Copy the key - you'll need it in the next steps

## Step 2: Test Locally (Optional but Recommended)

```bash
# Navigate to the scraper directory
cd scraper

# Install Python dependencies
pip install -r requirements.txt

# Set your API key (replace with your actual key)
export EBIRD_API_KEY="your-api-key-here"

# Run the test script
./test_scraper.sh

# Go back to project root
cd ..

# Start a local web server
python3 -m http.server 8000

# Open http://localhost:8000 in your browser
```

## Step 3: Deploy to GitHub Pages

### Option A: Create New Repository

1. Create a new repository on GitHub called `nyc-rare-birds`
2. Make it public
3. Initialize with README: No
4. Push this code:

```bash
cd nyc-rare-birds
git init
git add .
git commit -m "Initial commit: NYC Rare Birds Map"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/nyc-rare-birds.git
git push -u origin main
```

### Option B: Fork This Repository

1. Click "Fork" on the original repository
2. Clone your fork:

```bash
git clone https://github.com/YOUR-USERNAME/nyc-rare-birds.git
cd nyc-rare-birds
```

## Step 4: Configure GitHub

### Add Your API Key as a Secret

1. Go to your repository on GitHub
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Name: `EBIRD_API_KEY`
5. Value: Paste your eBird API key
6. Click **Add secret**

### Enable GitHub Pages

1. Go to **Settings** > **Pages**
2. Under "Source", select:
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/ (root)**
3. Click **Save**

## Step 5: Run the First Update

1. Go to the **Actions** tab
2. Click on **Update Bird Sightings** workflow
3. Click **Run workflow** dropdown
4. Click **Run workflow** button
5. Wait 2-5 minutes for it to complete
6. Check the Actions log to ensure it succeeded

## Step 6: View Your Site!

Your site will be live at:
```
https://YOUR-USERNAME.github.io/nyc-rare-birds
```

It may take a few minutes for GitHub Pages to deploy after the first run.

## Verification Checklist

✅ eBird API key obtained
✅ GitHub repository created
✅ API key added to GitHub Secrets
✅ GitHub Pages enabled
✅ First workflow run completed successfully
✅ Site is live and displays bird sightings

## Troubleshooting

### "No bird sightings found" message

- The scraper may not have run yet
- Go to Actions tab and manually trigger the workflow
- Check if `data/birds.json` exists in your repository

### Workflow fails with "API key not found"

- Make sure you added `EBIRD_API_KEY` to GitHub Secrets (not variables)
- The name must be exactly `EBIRD_API_KEY`
- Try deleting and re-adding the secret

### Site shows 404 error

- Wait a few minutes for GitHub Pages to deploy
- Check Settings > Pages to ensure it's enabled
- Make sure you're using the correct URL format

### Map loads but no markers appear

- Check browser console (F12) for errors
- Verify `data/birds.json` has valid data
- Try refreshing the page

## What Happens Next?

- The scraper will run automatically every day at 4am EST
- New bird sightings will appear on your map
- Old sightings (7+ days) are automatically removed
- No maintenance required!

## Customization Ideas

- Change the map colors in `styles.css`
- Adjust the update schedule in `.github/workflows/update-birds.yml`
- Modify the data retention period in `scraper/scrape_ebird.py`
- Add more NYC regions to cover in `scraper/scrape_ebird.py`

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review the GitHub Actions logs for error messages
- Test the scraper locally using the instructions above
- Open an issue on GitHub if you're stuck

---

Happy birdwatching! 🦅
