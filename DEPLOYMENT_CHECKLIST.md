# Deployment Checklist

Use this checklist to deploy your NYC Rare Birds Map to GitHub Pages.

## Pre-Deployment

### Local Setup (Optional)
- [ ] Install Python 3.11 or higher
- [ ] Install dependencies: `cd scraper && pip install -r requirements.txt`
- [ ] Get eBird API key from https://ebird.org/api/keygen
- [ ] Create `.env` file from `.env.example`
- [ ] Test scraper locally: `./scraper/test_scraper.sh`
- [ ] Test frontend locally: `python3 -m http.server 8000`

## GitHub Setup

### 1. Repository Creation
- [ ] Create new GitHub repository named `nyc-rare-birds`
- [ ] Make repository **public** (required for free GitHub Pages)
- [ ] Do NOT initialize with README (we already have one)

### 2. Push Code to GitHub
```bash
cd nyc-rare-birds
git init
git add .
git commit -m "Initial commit: NYC Rare Birds Map"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/nyc-rare-birds.git
git push -u origin main
```

- [ ] Code pushed successfully to GitHub
- [ ] All files visible in repository

### 3. Add eBird API Key
- [ ] Go to repository Settings
- [ ] Navigate to: **Secrets and variables** > **Actions**
- [ ] Click **New repository secret**
- [ ] Name: `EBIRD_API_KEY` (exactly as shown)
- [ ] Value: Your eBird API key
- [ ] Click **Add secret**
- [ ] Verify secret appears in list (value will be hidden)

### 4. Enable GitHub Pages
- [ ] Go to repository Settings
- [ ] Navigate to: **Pages** (in left sidebar)
- [ ] Under "Source":
  - [ ] Select **Deploy from a branch**
  - [ ] Branch: **main**
  - [ ] Folder: **/ (root)**
- [ ] Click **Save**
- [ ] Note the URL shown (will be `https://YOUR-USERNAME.github.io/nyc-rare-birds`)

## First Run

### 5. Trigger Initial Workflow
- [ ] Go to **Actions** tab
- [ ] Click on **Update Bird Sightings** workflow (left sidebar)
- [ ] Click **Run workflow** button (right side)
- [ ] Select branch: **main**
- [ ] Click green **Run workflow** button
- [ ] Wait for workflow to start (refresh page)

### 6. Monitor Workflow
- [ ] Click on the running workflow
- [ ] Click on job: **scrape-and-update**
- [ ] Watch logs in real-time
- [ ] Verify all steps complete successfully:
  - [ ] Checkout repository
  - [ ] Set up Python
  - [ ] Install dependencies
  - [ ] Run scraper
  - [ ] Commit and push if changed

### 7. Check for Errors
- [ ] No red X marks in workflow
- [ ] "Run scraper" step shows bird sightings found
- [ ] "Commit and push" step shows file changes
- [ ] Workflow marked as completed (green checkmark)

## Verification

### 8. Verify Data
- [ ] Go to repository main page
- [ ] Navigate to `data/birds.json`
- [ ] File exists and was updated recently
- [ ] Contains actual bird sightings (not just sample data)
- [ ] Check `assets/cache/wikipedia-images/` for downloaded bird photos

### 9. Visit Your Site
- [ ] Go to: `https://YOUR-USERNAME.github.io/nyc-rare-birds`
- [ ] Wait up to 5 minutes for GitHub Pages to deploy
- [ ] Page loads successfully
- [ ] Map displays centered on NYC
- [ ] Bird markers visible on map
- [ ] Click a marker to see popup
- [ ] Popup shows:
  - [ ] Bird photo (or placeholder)
  - [ ] Bird name
  - [ ] Scientific name
  - [ ] Description
  - [ ] Location
  - [ ] Date
  - [ ] Observer name

### 10. Test Map Features
- [ ] Zoom in/out works
- [ ] Pan around map works
- [ ] Markers cluster when zoomed out
- [ ] Markers uncluster when zoomed in
- [ ] Heat map layer visible (colored gradient)
- [ ] All popups open correctly
- [ ] Images load (or show placeholder)
- [ ] Header shows "Birds of NYC" with bird icon
- [ ] Footer shows binocular man icon
- [ ] Footer shows "Last updated" timestamp
- [ ] Mobile responsive (if applicable)

## Post-Deployment

### 11. Schedule Verification
- [ ] Workflow is scheduled to run daily at 4am EST
- [ ] Check `.github/workflows/update-birds.yml` cron setting
- [ ] Confirm timezone is correct (9am UTC = 4am EST)

### 12. Monitor First Automatic Run
- [ ] Check Actions tab tomorrow after 4am EST
- [ ] Verify workflow ran automatically
- [ ] Confirm data was updated
- [ ] Visit site to see new sightings

### 13. Documentation
- [ ] Update README.md with your actual GitHub Pages URL
- [ ] Share URL with friends/colleagues
- [ ] Add link to eBird if you want to credit them more prominently

## Troubleshooting

### If workflow fails:
1. Check Actions logs for error messages
2. Verify `EBIRD_API_KEY` secret is set correctly
3. Test scraper locally with same API key
4. Check eBird API status: https://ebird.org

### If site doesn't load:
1. Wait 5-10 minutes after first push
2. Check GitHub Pages settings are correct
3. Verify repository is public
4. Check for error message in Pages settings

### If no birds appear:
1. Check `data/birds.json` exists and has data
2. Open browser console (F12) for JavaScript errors
3. Verify data format matches expected structure
4. Check if there were any rare bird sightings in NYC recently

### If images don't load:
1. Check `assets/cache/wikipedia-images/` has images
2. Verify image paths in `birds.json` are correct
3. Placeholder image should show as fallback
4. Check browser console for 404 errors

## Success Criteria

Your deployment is successful when:
- ✅ Site is live and accessible at GitHub Pages URL
- ✅ Map loads centered on NYC
- ✅ Bird markers appear with correct locations
- ✅ Popups show bird information and photos
- ✅ Workflow runs automatically daily
- ✅ Data updates without manual intervention

## Maintenance

### Regular Checks (Optional)
- Check site weekly to ensure it's still updating
- Monitor GitHub Actions for any failures
- Watch eBird API limits (shouldn't be an issue)
- Clear old images from cache if repository size grows too large

### Updates
- To change update schedule: Edit `.github/workflows/update-birds.yml`
- To change data retention: Edit `scraper/scrape_ebird.py`
- To modify map styling: Edit `styles.css`
- To change map behavior: Edit `map.js`

---

## Quick Reference

**Site URL**: `https://YOUR-USERNAME.github.io/nyc-rare-birds`

**API Key Source**: https://ebird.org/api/keygen

**Actions Tab**: `https://github.com/YOUR-USERNAME/nyc-rare-birds/actions`

**Pages Settings**: `https://github.com/YOUR-USERNAME/nyc-rare-birds/settings/pages`

**Secrets Settings**: `https://github.com/YOUR-USERNAME/nyc-rare-birds/settings/secrets/actions`

---

**Questions?** Check README.md or QUICKSTART.md for help.

**Issues?** Review the Troubleshooting section above.

**Need support?** Open an issue on GitHub.
