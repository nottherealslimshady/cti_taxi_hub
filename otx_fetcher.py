# otx_fetcher.py
# Fetches pulses from AlienVault OTX API and converts them to STIX 2.x

import requests
import json
from stix2 import Indicator, Observable, Bundle, TLP_WHITE # Added TLP_WHITE import
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AlienVaultOTXFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://otx.alienvault.com/api/v1"
        self.headers = {
            "X-OTX-API-KEY": self.api_key,
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
                logging.warning("AlienVault OTX rate limit hit. Waiting for 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint, params) # Retry after delay
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for {endpoint}: {e}")
            return None

    def fetch_recent_pulses(self, limit=10):
        """Fetches recent public pulses from AlienVault OTX."""
        stix_objects = []
        logging.info(f"Fetching {limit} recent pulses from AlienVault OTX...")
        endpoint = "pulses/subscribed" # Or 'pulses/latest' for public
        params = {"limit": limit}
        data = self._make_request(endpoint, params)

        if data and 'results' in data:
            for pulse in data['results']:
                pulse_id = pulse.get('id')
                name = pulse.get('name', 'Unnamed Pulse')
                description = pulse.get('description', 'No description.')
                modified = pulse.get('modified')

                logging.info(f"Processing OTX Pulse: {name} (ID: {pulse_id})")

                for indicator_data in pulse.get('indicators', []):
                    indicator_type = indicator_data.get('type')
                    indicator_value = indicator_data.get('indicator')
                    if not indicator_value:
                        continue

                    # Map OTX indicator types to STIX observable types and patterns
                    observable = None
                    pattern = None
                    description_suffix = f" from OTX Pulse '{name}' (ID: {pulse_id})"

                    if indicator_type == 'IPv4':
                        observable = Observable(value=indicator_value, type='ipv4-addr')
                        pattern = f"[ipv4-addr:value = '{indicator_value}']"
                    elif indicator_type == 'IPv6':
                        observable = Observable(value=indicator_value, type='ipv6-addr')
                        pattern = f"[ipv6-addr:value = '{indicator_value}']"
                    elif indicator_type == 'domain':
                        observable = Observable(value=indicator_value, type='domain-name') # Corrected type to domain-name
                        pattern = f"[domain-name:value = '{indicator_value}']"
                    elif indicator_type == 'hostname': # Treat hostname as domain for simplicity
                        observable = Observable(value=indicator_value, type='domain-name') # Corrected type to domain-name
                        pattern = f"[domain-name:value = '{indicator_value}']"
                    elif indicator_type == 'URL':
                        observable = Observable(value=indicator_value, type='url')
                        pattern = f"[url:value = '{indicator_value}']"
                    elif indicator_type == 'FileHash-MD5':
                        observable = Observable(value=indicator_value, type='file', hashes={'MD5': indicator_value})
                        pattern = f"[file:hashes.'MD5' = '{indicator_value}']"
                    elif indicator_type == 'FileHash-SHA1':
                        observable = Observable(value=indicator_value, type='file', hashes={'SHA-1': indicator_value})
                        pattern = f"[file:hashes.'SHA-1' = '{indicator_value}']"
                    elif indicator_type == 'FileHash-SHA256':
                        observable = Observable(value=indicator_value, type='file', hashes={'SHA-256': indicator_value})
                        pattern = f"[file:hashes.'SHA-256' = '{indicator_value}']"
                    else:
                        logging.warning(f"Unsupported OTX indicator type: {indicator_type} for value: {indicator_value}")
                        continue

                    if observable and pattern:
                        indicator = Indicator(
                            pattern=pattern,
                            pattern_type="stix",
                            description=f"{indicator_type} indicator: {indicator_value}{description_suffix}",
                            valid_from=modified if modified else time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                            # Add TLP marking
                            object_marking_refs=[TLP_WHITE],
                            # You might add a relationship to the observable here if needed
                        )
                        stix_objects.extend([observable, indicator])
                        logging.info(f"Created STIX Indicator for {indicator_type}: {indicator_value}")

        return stix_objects
