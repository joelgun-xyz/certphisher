# 🚀 Quick Start for macOS

Get Certphisher running on your MacBook in under 5 minutes!

## Prerequisites

Just need Homebrew installed. If you don't have it:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## 1. Install Docker Desktop

```bash
brew install --cask docker
```

After installation, **open Docker Desktop** from your Applications folder and let it finish starting up (you'll see a whale icon in your menu bar).

## 2. Get the Code

```bash
# Clone the repository
git clone https://github.com/plonxyz/certphisher.git
cd certphisher

# Or if you already have it
cd certphisher
git pull
```

## 3. Setup Configuration

Using the Makefile (easiest):

```bash
make setup
```

This will:
- Copy `config.docker.ini` to `config.ini`
- Build Docker images
- Prepare everything

**Now edit the config file:**

```bash
nano config.ini
# or
open -e config.ini  # Opens in TextEdit
```

**Add your API keys:**
- Line 4: Replace `YOUR_VIRUSTOTAL_API_KEY_HERE` with your actual VirusTotal key
- Line 7: Replace `YOUR_URLSCAN_API_KEY_HERE` with your actual urlscan.io key

Get API keys here:
- VirusTotal: https://developers.virustotal.com/reference
- urlscan.io: https://urlscan.io/about-api/

**Save and close the file.**

## 4. Start Everything

```bash
make start
```

That's it! ✅

## 5. Access the Dashboard

Open your browser:

**Main Dashboard:** http://localhost:5000

**Settings Page:** http://localhost:5000/settings

## 📊 What You'll See

### In the Terminal

You'll see logs showing:
- Certificate stream connections
- Domains being analyzed
- Phishing scores
- Brand mismatch detections

### In the Browser

- **Dashboard**: Last 25 detected suspicious domains
- **Statistics**: Critical, High, Medium severity counts
- **Brand Detection**: Logos, mismatches, similarity scores
- **Settings**: Add your own brands, upload logos, capture screenshots

## 🎮 Common Commands

```bash
# View logs in real-time
make logs

# View just backend (certificate monitoring)
make logs-backend

# View just frontend (web dashboard)
make logs-frontend

# Check status
make status

# Stop everything
make stop

# Restart
make restart

# Stop and remove everything (keeps data)
make clean

# MongoDB shell
make mongo-shell
```

## 🔧 Add Your First Brand

1. Open http://localhost:5000/settings
2. Fill in the form:
   - **Brand Keyword:** `bankxyz` (or your company name)
   - **Full Brand Name:** `Bank XYZ Corporation`
   - **Official Website:** `https://www.bankxyz.com`
3. Click "Choose File" and upload your company logo
4. Click "Add Brand"
5. Click "📸 Capture Screenshot" to grab a reference screenshot

Now whenever a domain with "bankxyz" appears, it will:
- Compare images against your uploaded logo
- Check if the brand name appears on the site
- Compare the page layout against your screenshot
- Flag as suspicious if there's a mismatch

## 🐛 Troubleshooting

### "Cannot connect to the Docker daemon"

**Problem:** Docker Desktop isn't running

**Solution:**
1. Open Docker Desktop from Applications
2. Wait for the whale icon to appear in menu bar
3. Try `make start` again

### "Port 5000 already in use"

**Problem:** Another app is using port 5000 (maybe AirPlay Receiver on macOS Monterey+)

**Solution 1 - Disable AirPlay Receiver:**
1. System Preferences → Sharing
2. Uncheck "AirPlay Receiver"

**Solution 2 - Use different port:**

Edit `docker-compose.yml`:
```yaml
certphisher-frontend:
  ports:
    - "5001:5000"  # Changed from 5000:5000
```

Then access at http://localhost:5001

### "No detections showing up"

**Problem:** Need to wait for certificates to appear in the stream

**Solution:**
- It can take 5-10 minutes for first detections
- Check backend logs: `make logs-backend`
- Make sure you see "Connected to certstream"
- Suspicious domains will appear when detected

### Screenshots not working

**Problem:** Selenium/Chrome issue

**Solution:** Already included in Docker, but verify:
```bash
docker-compose exec certphisher-frontend which chromium
```

Should show: `/usr/bin/chromium`

## 📈 Performance on macOS

### For Apple Silicon (M1/M2/M3)

Docker runs great on Apple Silicon! The images will automatically build for ARM64.

**Recommended Settings in Docker Desktop:**
- Resources → Memory: 4-8 GB
- Resources → CPUs: 2-4 cores
- Resources → Disk: 20 GB

### For Intel Macs

Same as above, but x86_64 images.

**Recommended Settings:**
- Resources → Memory: 4-8 GB
- Resources → CPUs: 2-4 cores

## 🔍 Monitoring

### Watch for Detections

```bash
# Follow backend logs
make logs-backend
```

Look for lines like:
```
[!] Suspicious: paypal-secure-login.tk (score=125) [CA: Let's Encrypt]
[!] Logo Mismatch: Brand 'paypal' in domain but not on site - score +20
```

### Check Database

```bash
# Access MongoDB
make mongo-shell

# Run queries
db.sites.find().limit(5).pretty()
db.sites.countDocuments({certphisher_score: {$gt: 100}})
db.brands.find().pretty()
```

## 🧹 Cleanup

### Stop but Keep Data

```bash
make stop
# or
docker-compose stop
```

### Remove Containers but Keep Data

```bash
make clean
# or
docker-compose down
```

### Remove Everything Including Data

```bash
make clean-all
# or
docker-compose down -v
```

## 🔄 Updates

When there are code updates:

```bash
cd certphisher
git pull
make update
```

This will:
- Pull latest code
- Rebuild images
- Restart services

## 💾 Backups

### Backup MongoDB Data

```bash
make backup
```

Backups are saved to `./backups/backup_YYYYMMDD_HHMMSS/`

### Backup Logos/Screenshots

```bash
tar -czf uploads_backup.tar.gz app/uploads/
```

## 🎯 Next Steps

1. **Monitor the stream** - Watch `make logs-backend` for detections
2. **Add your brands** - http://localhost:5000/settings
3. **Check the dashboard** - http://localhost:5000
4. **Review detections** - Analyze phishing attempts
5. **Tune scoring** - Edit `suspicious.yaml` and `external.yaml`
6. **Setup Slack** - Get notifications (optional)

## 📚 More Documentation

- **Full Docker Guide:** [DOCKER_README.md](./DOCKER_README.md)
- **Enhanced Features:** [README_ENHANCED.md](./README_ENHANCED.md)
- **Settings Page:** [SETTINGS_GUIDE.md](./SETTINGS_GUIDE.md)
- **Changelog:** [CHANGELOG.md](./CHANGELOG.md)

## ❓ Need Help?

1. Check logs: `make logs`
2. Check status: `make status`
3. Verify config: `cat config.ini`
4. Test MongoDB: `make mongo-shell`

Still stuck? Check the full [DOCKER_README.md](./DOCKER_README.md) for detailed troubleshooting.

---

**Enjoy hunting phishers!** 🎣🔒
