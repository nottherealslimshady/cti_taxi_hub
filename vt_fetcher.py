# vt_fetcher.py
# Fetches indicators from VirusTotal API and converts them to STIX 2.x

import requests
import json
from stix2 import Indicator, Observable, Bundle, TLP_WHITE # Added TLP_WHITE import
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VirusTotalFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"
        self.headers = {
            "x-apikey": self.api_key,
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
                logging.warning("VirusTotal rate limit hit. Waiting for 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint, params) # Retry after delay
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for {endpoint}: {e}")
            return None

    def fetch_recent_indicators(self, limit=10):
        """
        Fetches recent file, URL, domain, and IP indicators from VirusTotal.
        Note: VirusTotal's public API has significant limitations on "recent" data.
        This will typically get recent *detections* or *analyses* rather than a firehose of new IOCs.
        For a true "feed," a premium VT subscription is usually required.
        For this project, we'll simulate by fetching general file/URL/domain/IP info
        which might have a recent analysis date.
        """
        stix_objects = []
        logging.info(f"Fetching {limit} recent indicators from VirusTotal...")

        # Dummy data representing what VT might return
        # In a real scenario, you'd feed specific observables to VT for lookup
        # or use a premium feed for bulk recent data.
        dummy_iocs = [
            {"value": "8.8.8.8", "type": "ipv4-addr", "source": "VirusTotal", "context": "Malicious IP (dummy)"},
            {"value": "malicious.example.com", "type": "domain", "source": "VirusTotal", "context": "Malicious Domain (dummy)"},
            {"value": "http://phishing.example.org/login", "type": "url", "source": "VirusTotal", "context": "Phishing URL (dummy)"},
            {"value": "d41d8cd98f00b204e9800998ecf8427e", "type": "file-hash", "source": "VirusTotal", "context": "Known bad MD5 (dummy)"}
        ]

        for ioc in dummy_iocs:
            # Create STIX Observable
            if ioc['type'] == 'ipv4-addr':
                observable = Observable(value=ioc['value'], type='ipv4-addr')
                pattern = f"[ipv4-addr:value = '{ioc['value']}']"
            elif ioc['type'] == 'domain':
                observable = Observable(value=ioc['value'], type='domain-name') # Corrected type to domain-name
                pattern = f"[domain-name:value = '{ioc['value']}']"
            elif ioc['type'] == 'url':
                observable = Observable(value=ioc['value'], type='url')
                pattern = f"[url:value = '{ioc['value']}']"
            elif ioc['type'] == 'file-hash':
                observable = Observable(value=ioc['value'], type='file', hashes={'MD5': ioc['value']})
                pattern = f"[file:hashes.'MD5' = '{ioc['value']}']"
            else:
                logging.warning(f"Unsupported IOC type: {ioc['type']}")
                continue

            # Create STIX Indicator
            indicator = Indicator(
                pattern=pattern,
                pattern_type="stix",
                description=f"{ioc['context']} from {ioc['source']}",
                valid_from=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                object_marking_refs=[TLP_WHITE], # Added TLP marking
                # You might add a relationship to the observable here if needed
            )
            stix_objects.extend([observable, indicator])
            logging.info(f"Created STIX Indicator for {ioc['type']}: {ioc['value']}")

        return stix_objects
