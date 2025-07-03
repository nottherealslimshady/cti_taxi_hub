# abuseipdb_fetcher.py
# Fetches IP reputation from AbuseIPDB API and converts to STIX 2.x

import requests
import json
from stix2 import Indicator, Observable, Bundle, TLP_WHITE # Added TLP_WHITE import
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AbuseIPDBFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.abuseipdb.com/api/v2"
        self.headers = {
            "Key": self.api_key,
            "Accept": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, endpoint, params=None):
        """Helper to make API requests with rate limiting."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error for {endpoint}: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429: # Too Many Requests
                logging.warning("AbuseIPDB rate limit hit. Waiting for 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint, params) # Retry after delay
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for {endpoint}: {e}")
            return None

    def check_ip(self, ip_address, max_age_in_days=90):
        """Checks the reputation of a single IP address."""
        endpoint = "check"
        params = {
            "ip": ip_address,
            "maxAgeInDays": max_age_in_days,
            "verbose": "" # Request verbose output
        }
        data = self._make_request(endpoint, params)
        if data and 'data' in data:
            return data['data']
        return None

    def fetch_recent_indicators(self, ip_list=None):
        """
        Fetches reputation for a list of IP addresses from AbuseIPDB.
        Since AbuseIPDB's free API is primarily for checking specific IPs,
        we use a predefined list for demonstration. In a real scenario,
        these IPs would come from other feeds or internal logs.
        """
        if ip_list is None:
            # Example IPs (replace with real known bad IPs for better testing, but be careful)
            # These are just examples to demonstrate the API call.
            # Do NOT use these to report actual abuse unless verified.
            ip_list = [
                "185.192.126.111", # Example: Known malicious IP from a public list
                "192.168.1.1",     # Example: Private IP, should have no reports
                "8.8.4.4"          # Example: Google DNS, should be clean
            ]

        stix_objects = []
        logging.info(f"Checking {len(ip_list)} IP addresses with AbuseIPDB...")

        for ip_address in ip_list:
            ip_info = self.check_ip(ip_address)
            if ip_info:
                abuse_score = ip_info.get('abuseConfidenceScore', 0)
                is_whitelisted = ip_info.get('isWhitelisted', False)
                total_reports = ip_info.get('totalReports', 0)
                last_reported = ip_info.get('lastReportedAt')

                description = (
                    f"AbuseIPDB Report for {ip_address}: "
                    f"Score: {abuse_score}%, Reports: {total_reports}, "
                    f"Whitelisted: {is_whitelisted}. "
                    f"Last reported: {last_reported if last_reported else 'N/A'}."
                )

                # Create STIX Observable
                observable = Observable(value=ip_address, type='ipv4-addr')

                # Create STIX Indicator
                # Pattern based on IP value and potentially score threshold
                pattern = f"[ipv4-addr:value = '{ip_address}']"
                if abuse_score >= 50 and not is_whitelisted: # Example threshold
                    pattern = f"[ipv4-addr:value = '{ip_address}'] AND [x-abuseipdb:abuse_confidence_score >= 50]"
                    description = f"Malicious IP from AbuseIPDB: {ip_address}. " + description
                else:
                    description = f"IP from AbuseIPDB: {ip_address}. " + description

                indicator = Indicator(
                    pattern=pattern,
                    pattern_type="stix",
                    description=description,
                    valid_from=last_reported if last_reported else time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    object_marking_refs=[TLP_WHITE],
                    # Add custom properties for more details if needed
                    custom_properties={
                        'x_abuseipdb_abuse_confidence_score': abuse_score,
                        'x_abuseipdb_is_whitelisted': is_whitelisted,
                        'x_abuseipdb_total_reports': total_reports,
                        'x_abuseipdb_last_reported_at': last_reported
                    }
                )
                stix_objects.extend([observable, indicator])
                logging.info(f"Created STIX Indicator for IP: {ip_address} (Score: {abuse_score}%)")
            else:
                logging.warning(f"Could not get AbuseIPDB info for IP: {ip_address}")

        return stix_objects
