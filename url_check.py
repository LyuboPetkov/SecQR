import os
import re
import requests
import cv2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def decode_qr_code(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    return data

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def check_url_safety(url):
    google_api_key = os.getenv("GOOGLE_API_KEY")
    virustotal_api_key = os.getenv("VIRUSTOTAL_API_KEY")

    if not google_api_key:
        return "Google API key not found. Please set the GOOGLE_API_KEY environment variable.", None

    if not virustotal_api_key:
        return "VirusTotal API key not found. Please set the VIRUSTOTAL_API_KEY environment variable.", None

    if not re.match(r'^(?:http|ftp)s?://', url):
        url = 'http://' + url

    if not is_valid_url(url):
        url = url.replace('http://', '').replace('https://', '')
        return "URL not found", url

    google_endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={google_api_key}"
    google_payload = {
        "client": {
            "clientId": "secure-url-check",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [
                {"url": url}
            ]
        }
    }
    google_response = requests.post(google_endpoint, json=google_payload)
    try:
        google_result = google_response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Google Safe Browsing API response is not JSON: {google_response.text}")
        return "Error processing URL with Google Safe Browsing API", url

    if 'matches' in google_result:
        return "URL is dangerous", url

    virustotal_endpoint = "https://www.virustotal.com/vtapi/v2/url/report"
    virustotal_params = {
        "apikey": virustotal_api_key,
        "resource": url
    }
    virustotal_response = requests.get(virustotal_endpoint, params=virustotal_params)
    try:
        virustotal_result = virustotal_response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"VirusTotal API response is not JSON: {virustotal_response.text}")
        return "Error processing URL with VirusTotal API", url

    if virustotal_result.get('response_code') == 1 and virustotal_result.get('positives') > 0:
        return "URL is dangerous", url

    return "URL is not dangerous", url

def check_qr_url(filepath):
    url = decode_qr_code(filepath)
    if url is None or url == "":
        return "QR not found", None
    
    result, checked_url = check_url_safety(url)
    return result, checked_url

if __name__ == "__main__":
    filepath = "check_url_qr.png"
    result, checked_url = check_qr_url(filepath)
    print(f"Result: {result}")
    print(f"Checked URL: {checked_url}")
