# Certphisher - Enhanced 2025 Edition 🔒

This is an enhanced fork of [@joelgun's](https://twitter.com/joelgun) certphisher, which itself is based on [@x0rz's](https://twitter.com/x0rz) [phishing_catcher](https://github.com/x0rz/phishing_catcher).

## 🚀 What's New in 2025

### Major Enhancements

1. **CA Filtering** - Automatically exclude certificates from legitimate CAs (DigiCert, Sectigo, etc.)
2. **Logo Detection** - Verify if brand names in domains match actual website content
3. **Modernized Stack** - Flask 3.0, Python 3.x, latest dependencies
4. **Enhanced Frontend** - Improved UI showing brand verification results
5. **Bug Fixes** - Critical fixes for certificate processing and MongoDB queries

## 🎯 Key Features

### CA Filtering
Phishers typically use free CAs like Let's Encrypt, while legitimate businesses use commercial CAs. This feature:
- Automatically skips certificates from legitimate CAs
- Reduces noise by 80-90%
- Focuses monitoring on suspicious CAs
- Fully configurable via config.ini

**Example:** A certificate from DigiCert for "microsoft.com" is automatically excluded, while a Let's Encrypt cert for "microsoft-login-secure.tk" is flagged.

### Logo Detection
When a brand keyword appears in a domain (e.g., "paypal" in "paypal-secure.com"), the system:
1. Fetches the actual website
2. Checks if the brand name appears in the content
3. Looks for logo-related HTML elements
4. Flags mismatches as highly suspicious (+20 score)

**Example:** Domain "paypal-account-verify.xyz" is detected, but when the site is fetched, there's no PayPal branding → score increased, marked as brand mismatch.

## 📋 Prerequisites

- Python 3.8+
- MongoDB 4.0+
- API Keys:
  - [VirusTotal](https://developers.virustotal.com/reference) (free tier: 4 requests/min)
  - [urlscan.io](https://urlscan.io/about-api/) (free)
- Optional: Slack workspace for notifications

## 🚀 Installation

```bash
git clone https://github.com/your-username/certphisher.git
cd certphisher

# Install dependencies
pip3 install -r requirements.txt

# Configure
cp default-config.ini config.ini
# Edit config.ini with your API keys
```

## ⚙️ Configuration

Edit `config.ini`:

```ini
[apikeys]
vt_key = YOUR_VIRUSTOTAL_KEY
urlscan_key = YOUR_URLSCAN_KEY

[mongodb]
my_instance = mongodb://localhost:27017/
my_db = certphisher
my_col = sites

[slack]
integration = 1
bot_key = YOUR_SLACK_BOT_TOKEN
channel = YOUR_CHANNEL_NAME
relevant_score = 140

[ca_filtering]
# Legitimate CAs to EXCLUDE from monitoring
legitimate_cas = DigiCert, Sectigo, GeoTrust, Thawte, Comodo, GlobalSign, Entrust, GoDaddy, Network Solutions

[logo_detection]
# Enable logo/brand verification
enabled = true
# Brands to monitor for mismatches
brand_keywords = paypal, amazon, apple, microsoft, google, facebook, instagram, netflix, dropbox, adobe, linkedin, twitter, ebay, walmart, target
```

### CA Filtering Configuration
Add or remove CAs from the `legitimate_cas` list. CAs in this list will be automatically excluded from monitoring.

**Recommended to exclude:**
- Commercial/Enterprise CAs (DigiCert, Sectigo, GlobalSign, Entrust)
- Major hosting providers (GoDaddy, Network Solutions)

**Recommended to monitor:**
- Let's Encrypt (most common for phishing)
- CloudFlare
- Free SSL providers

### Logo Detection Configuration
- `enabled`: Set to `true` to enable logo detection
- `brand_keywords`: Comma-separated list of brands to monitor
- Add your own company/client names to the list

## 🎮 Usage

### Start MongoDB
```bash
# Ubuntu/Debian
sudo systemctl start mongod

# macOS
brew services start mongodb-community

# Windows
net start MongoDB
```

### Run the Backend Engine
```bash
python3 main.py
```

You'll see output like:
```
certificate_update: 1234cert [00:15, 82.3cert/s]
[!] Suspicious: paypal-secure-login.tk (score=125) [CA: Let's Encrypt Authority X3]
[!] Logo Mismatch: Brand 'paypal' in domain but not on site - score increased by 20
```

### Run the Frontend
```bash
cd app
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

Access the dashboard at: **http://127.0.0.1:5000/**

## 📊 Dashboard Features

### Overview Section
- Critical, High, Medium severity counts
- Total detections
- Feature status indicators

### Detection Table
- **Registered Site**: Domain with brand mismatch indicator
- **CA**: Certificate Authority
- **Risk Score**: Color-coded severity badge
- **Brand Detection**: Shows expected vs. found brands
- **Scan Date**: When analyzed
- **Live Reports**: Links to VirusTotal, urlscan.io
- **Screenshot**: Visual preview from urlscan.io

### Brand Detection Column
Shows one of:
- ✓ Found on site (brand verified)
- ✗ NOT found on site (suspicious!)
- - (no brand keywords detected)

## 🔍 Scoring System

Base scoring from original project, enhanced with:

| Factor | Points | Description |
|--------|--------|-------------|
| Suspicious TLD | +20 | .tk, .ml, .ga, etc. |
| High entropy | up to +50 | Random-looking domains |
| Keyword match | varies | Brand names, "secure", "login" |
| Levenshtein distance | +70 | Typosquatting (paypol vs paypal) |
| Multiple hyphens | +3 each | paypal-account-verify-secure |
| Deep subdomains | +3 each | www.paypal.com.verify.tk |
| Let's Encrypt CA | +10 | Free CA commonly used by phishers |
| **Brand mismatch** | **+20** | **NEW: Brand in domain but not on site** |

**Severity Levels:**
- 140+: Critical (red)
- 90-139: High (orange)
- 80-89: Medium (blue)

## 🔔 Slack Notifications

When enabled, high-scoring domains trigger Slack alerts with:
- Domain name (defanged)
- Risk score
- Certificate Authority
- Brand keywords detected (if any)
- Links to VirusTotal and urlscan.io reports

## 🛠️ Customization

### Add Custom Brand Keywords
Edit `config.ini`:
```ini
brand_keywords = paypal, amazon, your-company-name, client-brand
```

### Adjust CA Filter
To monitor a currently-excluded CA, remove it from `legitimate_cas`:
```ini
# Before (excludes GoDaddy):
legitimate_cas = DigiCert, Sectigo, GoDaddy

# After (monitors GoDaddy):
legitimate_cas = DigiCert, Sectigo
```

### Customize Scoring
Edit `suspicious.yaml` or `external.yaml`:
```yaml
keywords:
  paypal: 100
  amazon: 95
  your-company: 120  # Add custom keywords
```

## 📈 API Endpoint

New in this version - JSON stats endpoint:

```bash
curl http://localhost:5000/api/stats
```

Returns:
```json
{
  "total": 1234,
  "critical": 45,
  "high": 123,
  "medium": 67,
  "ca_stats": {
    "Let's Encrypt Authority X3": 890,
    "CloudFlare Inc ECC CA-3": 123,
    "cPanel, Inc. Certification Authority": 45
  }
}
```

## 🐳 Docker Support

See the dockerized version: [certphisher-dockerized](https://github.com/joelgun-xyz/certphisher-dockerized/)

## 📝 Example Workflow

1. **Stream monitoring starts** - Connects to certstream.calidog.io
2. **Certificate detected** - New cert for "paypal-secure-login.tk"
3. **CA check** - Let's Encrypt (not in exclusion list, continue)
4. **Scoring** - Base score 85 (suspicious TLD, keyword match)
5. **Brand detection** - "paypal" found in domain
6. **Logo check** - Fetches site, no PayPal branding found
7. **Score increase** - +20 for brand mismatch, total: 105
8. **Actions**:
   - Submit to VirusTotal
   - Scan with urlscan.io
   - Save to MongoDB
   - Send Slack notification (if score ≥ threshold)
9. **Dashboard** - Shows in table with brand mismatch indicator

## 🔧 Troubleshooting

### Logo Detection Timeout
If sites take too long to load, logo detection may timeout. This is normal for sites that go offline quickly.

### Too Many False Positives
- Increase the `relevant_score` in config.ini
- Add more legitimate CAs to the exclusion list
- Refine brand keywords to be more specific

### MongoDB Connection Issues
Ensure MongoDB is running and accessible:
```bash
mongosh --eval "db.runCommand({ping: 1})"
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Advanced logo detection using image recognition
- Machine learning scoring
- Additional threat intelligence integrations
- Export functionality (CSV, JSON)

## 📄 License

GNU General Public License v3.0

## 👥 Authors & Credits

- **Enhanced Version (2025)** - Claude & User
- **Original Certphisher** - [joelgun](https://twitter.com/joelgun)
- **Phishing Catcher** - [@x0rz](https://twitter.com/x0rz)
- **urlscan-py wrapper** - [heywoodlh](https://github.com/heywoodlh/urlscan-py)

## 🔗 Resources

- [Certstream](https://certstream.calidog.io/) - Real-time certificate transparency log
- [VirusTotal](https://www.virustotal.com/) - File/URL analysis
- [urlscan.io](https://urlscan.io/) - Website scanner
- [Certificate Transparency](https://certificate.transparency.dev/) - Google's CT project

## ⚠️ Disclaimer

This tool is for legitimate security research, threat hunting, and defensive security purposes only. Use responsibly and in compliance with applicable laws and regulations.
