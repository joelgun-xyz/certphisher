# Settings Page Guide - Brand Monitoring Configuration

## Overview

The new Settings page allows you to configure brand monitoring with:
- **Logo uploads** for visual comparison
- **Reference website screenshots** for page similarity detection
- **Dynamic keyword management** through the web UI
- **Real-time brand configuration** without restarting the application

## Accessing Settings

Navigate to **http://localhost:5000/settings** or click the "Settings" link in the sidebar.

## Adding a New Brand

### Step 1: Fill in Brand Information

1. **Brand Keyword** (Required)
   - The keyword to detect in domain names
   - Example: `bankxyz`, `paypal`, `amazon`
   - Will be converted to lowercase automatically
   - Must be unique

2. **Full Brand Name** (Optional)
   - Display name for the brand
   - Example: "Bank XYZ Corporation"
   - If not provided, keyword will be used

3. **Official Website** (Optional but recommended)
   - The legitimate website URL
   - Example: `https://www.bankxyz.com`
   - Used for screenshot comparison

### Step 2: Upload Reference Logo

Click "Choose File" and select the company's official logo:
- **Supported formats:** PNG, JPG, JPEG, GIF, WebP
- **Max size:** 16MB
- **Best practices:**
  - Use high-quality logos (at least 200x200 pixels)
  - Transparent backgrounds (PNG) work best
  - Upload the most recognizable version of the logo

### Step 3: Submit

Click "Add Brand" to save the configuration.

## Screenshot Capture

Once a brand is added with an official website:

1. Click **"📸 Capture Screenshot"** to take a reference screenshot
2. The system uses headless Chrome to capture the page
3. Screenshot is stored and used for visual comparison with suspicious sites
4. Click **"🔄 Refresh Screenshot"** to update it anytime

### Requirements for Screenshots

- Chrome or Chromium browser must be installed
- Selenium WebDriver must be configured
- Network access to the reference website

## How It Works

### Logo Detection Process

When a suspicious domain is detected (e.g., `bankxyz-secure-login.tk`):

1. **Keyword Match:** System checks if "bankxyz" appears in the domain
2. **Website Fetch:** Downloads the suspicious site's homepage
3. **Image Extraction:** Extracts all images from the page
4. **Logo Comparison:** Compares each image against your uploaded reference logo using:
   - **SSIM (Structural Similarity Index):** Measures structural similarity
   - **Histogram Comparison:** Compares color distributions
5. **Similarity Scoring:** Calculates similarity scores (0-1, where 1 is identical)
6. **Threshold Check:** Logo match if similarity > 0.3
7. **Result:** If brand keyword in domain but logo NOT matched → Brand Mismatch (+20 phishing score)

### Screenshot Comparison

1. Reference screenshot stored when you click "Capture Screenshot"
2. When suspicious site detected, can compare layouts
3. Uses same image comparison algorithms
4. Detects cloned login pages and fake brand sites

### Text Detection

As a fallback, the system also:
- Checks if brand name appears in page text
- Looks for logo-related HTML elements
- Combines text and visual detection for accuracy

## Viewing Results

Detection results appear in the main dashboard:

- **Brand Detection Column:** Shows which brands were expected and found
- **Brand Mismatch Badge:** Red warning badge if brand in domain but not on site
- **Similarity Scores:** Hover over entries to see detailed similarity metrics

## Managing Brands

### Edit a Brand

Currently brands cannot be edited directly. To update:
1. Delete the existing brand
2. Re-add with updated information

### Delete a Brand

1. Click the red **✕** button on the brand card
2. Confirm deletion
3. Associated logo and screenshot files will be automatically deleted

### Best Practices

1. **Start with high-value brands:**
   - Your company/client brands
   - Common phishing targets (PayPal, Amazon, etc.)
   - Brands frequently seen in your industry

2. **Maintain up-to-date screenshots:**
   - Refresh screenshots monthly or after site redesigns
   - Legitimate sites change, phishing sites copy old versions

3. **Use clear, recognizable logos:**
   - Full logos work better than icons
   - Color logos better than black & white
   - Avoid logos with complex backgrounds

4. **Monitor performance:**
   - Too many brands = slower processing
   - Start with 10-20 brands, scale as needed
   - Remove brands that generate false positives

## Advanced Configuration

### Similarity Thresholds

The default similarity threshold is 0.3 (30% match). To adjust:

Edit `logo_detector.py`:
```python
'threshold_met': max_similarity > 0.3  # Change this value
```

Values:
- **0.1-0.3:** Loose matching (more detections, more false positives)
- **0.3-0.5:** Balanced (recommended)
- **0.5-0.8:** Strict matching (fewer false positives, may miss some)

### Disabling Logo Detection

In `config.ini`:
```ini
[logo_detection]
enabled = false
```

Brands remain in database but visual comparison is disabled.

## Troubleshooting

### "Error capturing screenshot"

**Cause:** Chrome/Chromium not installed or WebDriver issue

**Solutions:**
```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser chromium-chromedriver

# macOS
brew install --cask google-chrome
brew install chromedriver

# Or use webdriver-manager (included in requirements)
pip install webdriver-manager
```

### "Brand already exists"

**Cause:** Keyword is already in the database

**Solution:** Delete the existing brand first, or use a different keyword

### "Upload failed"

**Cause:** File type not allowed or too large

**Solutions:**
- Use PNG, JPG, JPEG, GIF, or WebP formats only
- Reduce file size (max 16MB)
- Compress images before uploading

### Low similarity scores

**Causes:**
- Logo quality poor
- Phishing site uses heavily modified logo
- Background colors don't match
- Logo partially obscured on phishing site

**Solutions:**
- Try uploading different logo variations
- Lower the similarity threshold
- Ensure reference logo is high quality

## Database Structure

Brands are stored in MongoDB `brands` collection:

```json
{
  "_id": ObjectId("..."),
  "keyword": "bankxyz",
  "name": "Bank XYZ Corporation",
  "reference_url": "https://www.bankxyz.com",
  "logo_path": "bankxyz_logo_1234567890.png",
  "reference_screenshot": "bankxyz_screenshot_1234567890.png",
  "created_at": ISODate("2025-01-15T10:30:00Z"),
  "updated_at": ISODate("2025-01-15T10:30:00Z")
}
```

## API Integration

Programmatically manage brands via API:

### Get All Brands
```bash
curl http://localhost:5000/api/brands
```

### Add Brand (programmatic)
Use MongoDB directly or extend the API with POST endpoints.

## Examples

### Example 1: Bank

```
Keyword: hsbc
Name: HSBC Bank
Reference URL: https://www.hsbc.com
Logo: hsbc-logo.png (red hexagon logo)
```

**Detection:**
- Domain: `hsbc-online-banking-secure.tk`
- Logo comparison: 0.15 (low similarity)
- Text detection: "HSBC" not found
- Result: ⚠ BRAND MISMATCH (+20 score)

### Example 2: E-commerce

```
Keyword: amazon
Name: Amazon
Reference URL: https://www.amazon.com
Logo: amazon-logo.png (smile logo)
```

**Detection:**
- Domain: `amazon-customer-service.xyz`
- Logo comparison: 0.82 (high similarity - legitimate affiliate)
- Text detection: "Amazon" found
- Result: ✓ Brand verified (no score increase)

### Example 3: Custom Company

```
Keyword: acmecorp
Name: ACME Corporation
Reference URL: https://www.acmecorp.com
Logo: acme-logo.png
Screenshot: Captured login page
```

**Detection:**
- Domain: `acmecorp-portal.com`
- Logo comparison: 0.05 (very low)
- Screenshot comparison: Different layout
- Text detection: "ACME" found but wrong context
- Result: ⚠ BRAND MISMATCH (+20 score)

## Performance Considerations

- **Logo comparison:** ~2-5 seconds per suspicious site
- **Screenshot comparison:** ~3-8 seconds (if enabled)
- **Image downloads:** Network dependent
- **Total overhead:** ~5-15 seconds per flagged domain

For high-volume environments:
- Limit brands to most critical
- Use worker queues for logo detection
- Cache results for repeated domains
- Adjust detection timeouts in `logo_detector.py`

## Security Notes

- Uploaded logos/screenshots stored in `app/uploads/`
- Filenames are sanitized and timestamped
- Files deleted when brand is removed
- No external access to upload directory by default
- Configure proper file permissions in production

## Support

For issues or questions:
1. Check logs: `app/uploads/` for file issues
2. MongoDB: `certphisher.brands` collection
3. Test detection: Add brand, trigger with test domain
4. Review detection results in dashboard Brand Detection column
