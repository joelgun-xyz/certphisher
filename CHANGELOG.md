# Changelog - Enhanced Certphisher

## Version 2.0 - 2025 Update

### 🚀 Major Features Added

#### 1. **CA Filtering**
- Automatically filters out certificates from legitimate Certificate Authorities
- Reduces noise by focusing on CAs commonly used by phishers (Let's Encrypt, etc.)
- Configurable list of legitimate CAs to exclude (DigiCert, Sectigo, GeoTrust, etc.)
- Significantly improves signal-to-noise ratio for phishing detection

#### 2. **Logo Detection & Brand Verification**
- Detects brand names in domains (paypal, amazon, microsoft, etc.)
- Automatically fetches websites and checks if expected brand appears in content
- Flags mismatches where brand name is in domain but not on the actual site
- Increases phishing score by +20 when brand mismatch is detected
- Configurable brand keyword list

#### 3. **Modernized Dependencies**
- Updated Flask from 1.0.2 to 3.0.3
- Updated pymongo to 4.10.1 with modern count_documents() methods
- Replaced deprecated slackclient with slack-sdk 3.33.4
- Added image processing libraries (Pillow, OpenCV, scikit-image)
- All dependencies updated to 2025 versions

#### 4. **Enhanced Frontend**
- Added new "Brand Detection" column showing logo verification results
- Visual indicators for brand mismatches (⚠ BRAND MISMATCH badge)
- Shows expected brands vs. brands found on site
- Cleaner, more compact button layout
- Enhanced overview section with feature descriptions

### 🐛 Bug Fixes
- Fixed critical typo in main.py line 248: `leaf_Cert` → `leaf_cert`
- Fixed deprecated MongoDB `.count()` methods → `.count_documents()`
- Updated Slack API calls from deprecated `api_call()` to `chat_postMessage()`

### 📝 Configuration Changes
New sections added to `config.ini`:

```ini
[ca_filtering]
legitimate_cas = DigiCert, Sectigo, GeoTrust, Thawte, Comodo, GlobalSign, Entrust, GoDaddy, Network Solutions

[logo_detection]
enabled = true
brand_keywords = paypal, amazon, apple, microsoft, google, facebook, instagram, netflix, dropbox, adobe, linkedin, twitter, ebay, walmart, target
```

### 💡 How It Works

**CA Filtering:**
- Certificates from legitimate CAs are automatically skipped
- Reduces processing load and focuses on suspicious certificates
- Customizable via config.ini

**Logo Detection:**
- When a brand keyword appears in a domain name, the system:
  1. Waits for the site to become accessible
  2. Fetches the homepage
  3. Checks if the brand name appears in the page content
  4. Checks for common logo-related HTML elements
  5. Flags as suspicious if brand is in domain but NOT on the site

This catches phishing sites like "paypal-secure-login.com" that don't actually display PayPal branding.

### 🔧 Technical Improvements
- Added comprehensive error handling for logo detection
- Logo detection results stored in MongoDB for analysis
- Enhanced Slack notifications include brand detection info
- Better logging and progress indicators
- API endpoint for statistics (/api/stats)

### 📦 Installation
All changes are backwards compatible. Simply:
1. Update your config.ini with new sections (see default-config.ini)
2. Run `pip3 install -r requirements.txt` to update dependencies
3. Restart the application

### 🎯 Benefits
- **Fewer False Positives:** CA filtering eliminates legitimate corporate certificates
- **Better Detection:** Logo detection catches sophisticated phishing attempts
- **Improved Accuracy:** Combined scoring system provides more reliable risk assessment
- **Modern Stack:** Updated dependencies ensure security and compatibility
