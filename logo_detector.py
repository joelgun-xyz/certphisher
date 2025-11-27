#!/usr/bin/env python
"""
Logo Detection and Image Comparison Module
Provides advanced logo detection using image similarity algorithms
"""

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import requests
from io import BytesIO
import pymongo
import os
from bs4 import BeautifulSoup
import re
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LogoDetector:
    def __init__(self, mongo_client, db_name='certphisher'):
        """Initialize logo detector with MongoDB connection"""
        self.myclient = mongo_client
        self.mydb = self.myclient[db_name]
        self.brands_col = self.mydb['brands']
        self.upload_dir = os.path.join(os.path.dirname(__file__), 'app', 'uploads')

    def get_brands_from_db(self):
        """Get all monitored brands from database"""
        return {brand['keyword']: brand for brand in self.brands_col.find()}

    def check_brand_in_domain(self, domain):
        """Check if any brand keywords appear in the domain"""
        domain_lower = domain.lower()
        brands_db = self.get_brands_from_db()
        found_brands = []

        for keyword in brands_db.keys():
            if keyword in domain_lower:
                found_brands.append({
                    'keyword': keyword,
                    'data': brands_db[keyword]
                })

        return found_brands

    def download_image(self, url):
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=10, verify=False)
            img = Image.open(BytesIO(response.content))
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except:
            return None

    def compare_images(self, img1, img2, method='ssim'):
        """
        Compare two images using structural similarity
        Returns similarity score (0-1, where 1 is identical)
        """
        try:
            # Resize images to same size for comparison
            height, width = 200, 200
            img1_resized = cv2.resize(img1, (width, height))
            img2_resized = cv2.resize(img2, (width, height))

            # Convert to grayscale
            gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)

            if method == 'ssim':
                # Structural Similarity Index
                score, _ = ssim(gray1, gray2, full=True)
                return score
            elif method == 'histogram':
                # Histogram comparison
                hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
                hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
                score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                return score
            else:
                return 0
        except:
            return 0

    def extract_images_from_page(self, domain):
        """Extract all images from a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(f"https://{domain}", headers=headers, timeout=10, verify=False)

            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')

            images = []
            for img in img_tags[:10]:  # Limit to first 10 images
                src = img.get('src', '')
                if src:
                    # Handle relative URLs
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = f"https://{domain}{src}"
                    elif not src.startswith('http'):
                        src = f"https://{domain}/{src}"

                    images.append(src)

            return images
        except:
            return []

    def compare_with_reference_logo(self, domain, brand_data):
        """Compare images on the domain with the reference logo"""
        if not brand_data.get('logo_path'):
            return None

        # Load reference logo
        logo_path = os.path.join(self.upload_dir, brand_data['logo_path'])
        if not os.path.exists(logo_path):
            return None

        reference_logo = cv2.imread(logo_path)
        if reference_logo is None:
            return None

        # Extract images from the suspicious domain
        page_images = self.extract_images_from_page(domain)

        max_similarity = 0
        matched_url = None

        for img_url in page_images:
            site_image = self.download_image(img_url)
            if site_image is not None:
                similarity = self.compare_images(reference_logo, site_image)
                if similarity > max_similarity:
                    max_similarity = similarity
                    matched_url = img_url

        return {
            'max_similarity': float(max_similarity),
            'matched_image_url': matched_url,
            'threshold_met': max_similarity > 0.3,  # Logo similarity threshold
            'total_images_checked': len(page_images)
        }

    def compare_with_reference_screenshot(self, domain, brand_data):
        """Compare page screenshot with reference screenshot"""
        if not brand_data.get('reference_screenshot'):
            return None

        # Load reference screenshot
        screenshot_path = os.path.join(self.upload_dir, brand_data['reference_screenshot'])
        if not os.path.exists(screenshot_path):
            return None

        reference_screenshot = cv2.imread(screenshot_path)
        if reference_screenshot is None:
            return None

        # Capture screenshot of suspicious site
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(f"https://{domain}", headers=headers, timeout=10, verify=False)

            # For simple comparison, we'll use a headless screenshot approach
            # In production, this would use Selenium like in the frontend
            # For now, we'll skip actual screenshot and just note it's available

            return {
                'screenshot_comparison_available': True,
                'reference_screenshot_exists': True,
                'note': 'Full screenshot comparison requires Selenium runtime'
            }
        except:
            return None

    def detect_logo_on_site(self, domain, siteid):
        """
        Enhanced logo detection with image comparison
        Returns detection results with similarity scores
        """
        found_brands = self.check_brand_in_domain(domain)

        if not found_brands:
            return None

        results = {
            'detected_brands': [],
            'logo_comparisons': [],
            'overall_mismatch': False,
            'confidence_score': 0
        }

        for brand_info in found_brands:
            keyword = brand_info['keyword']
            brand_data = brand_info['data']

            brand_result = {
                'keyword': keyword,
                'text_found': False,
                'logo_matched': False,
                'similarity_score': 0
            }

            # Check if brand name appears in page text
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(f"https://{domain}", headers=headers, timeout=10, verify=False)
                page_content = response.text.lower()
                brand_result['text_found'] = keyword in page_content
            except:
                pass

            # Compare with reference logo if available
            if brand_data.get('logo_path'):
                logo_comparison = self.compare_with_reference_logo(domain, brand_data)
                if logo_comparison:
                    brand_result['logo_matched'] = logo_comparison['threshold_met']
                    brand_result['similarity_score'] = logo_comparison['max_similarity']
                    brand_result['logo_comparison'] = logo_comparison

            # Compare with reference screenshot if available
            if brand_data.get('reference_screenshot'):
                screenshot_comp = self.compare_with_reference_screenshot(domain, brand_data)
                if screenshot_comp:
                    brand_result['screenshot_comparison'] = screenshot_comp

            results['detected_brands'].append(brand_result)

        # Determine overall mismatch
        # If brand in domain but neither text nor logo found, it's suspicious
        for brand in results['detected_brands']:
            if not brand['text_found'] and not brand['logo_matched']:
                results['overall_mismatch'] = True
                break

        # Calculate confidence score
        total_brands = len(results['detected_brands'])
        matched_brands = sum(1 for b in results['detected_brands'] if b['text_found'] or b['logo_matched'])
        results['confidence_score'] = (total_brands - matched_brands) / total_brands if total_brands > 0 else 0

        # Store results in database
        if siteid:
            self.mydb['sites'].update_one(
                {"_id": siteid},
                {"$set": {"logo_detection_v2": results}}
            )

        return results
