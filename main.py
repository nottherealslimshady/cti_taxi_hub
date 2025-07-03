# main.py
# Orchestrates fetching from CTI feeds and publishing to OpenTAXII

import time
import logging
from vt_fetcher import VirusTotalFetcher
from otx_fetcher import AlienVaultOTXFetcher
from abuseipdb_fetcher import AbuseIPDBFetcher
from taxii_publisher import TAXIIPublisher
from config import (
    VIRUSTOTAL_API_KEY, ALIENVAULT_OTX_API_KEY, ABUSEIPDB_API_KEY,
    OPENTAXII_SERVER_URL, OPENTAXII_COLLECTION_ID, OPENTAXII_USERNAME, OPENTAXII_PASSWORD
)
from stix2 import Bundle

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_collection_and_publishing():
    logging.info("Starting CTI collection and publishing cycle...")

    # Initialize fetchers
    vt_fetcher = VirusTotalFetcher(VIRUSTOTAL_API_KEY)
    otx_fetcher = AlienVaultOTXFetcher(ALIENVAULT_OTX_API_KEY)
    abuseipdb_fetcher = AbuseIPDBFetcher(ABUSEIPDB_API_KEY)

    # Initialize TAXII Publisher
    taxii_publisher = TAXIIPublisher(
        OPENTAXII_SERVER_URL,
        OPENTAXII_COLLECTION_ID,
        OPENTAXII_USERNAME,
        OPENTAXII_PASSWORD
    )

    all_stix_objects = []

    # Fetch from VirusTotal
    if VIRUSTOTAL_API_KEY and VIRUSTOTAL_API_KEY != '513bf61cf011c015a0a5124ae7aa140412381e6b2115907fcfc500547e573fa2':
        logging.info("Fetching from VirusTotal...")
        vt_stix = vt_fetcher.fetch_recent_indicators(limit=5) # Reduced limit for free tier
        all_stix_objects.extend(vt_stix)
        logging.info(f"Collected {len(vt_stix)} STIX objects from VirusTotal.")
    else:
        logging.warning("VirusTotal API key not configured. Skipping VirusTotal fetch.")

    # Fetch from AlienVault OTX
    if ALIENVAULT_OTX_API_KEY and ALIENVAULT_OTX_API_KEY != 'cc10d2976dbe84523c003c2b0b3bdb9ba375683d1b3469aec36438aa2c98acec':
        logging.info("Fetching from AlienVault OTX...")
        otx_stix = otx_fetcher.fetch_recent_pulses(limit=5) # Reduced limit for free tier
        all_stix_objects.extend(otx_stix)
        logging.info(f"Collected {len(otx_stix)} STIX objects from AlienVault OTX.")
    else:
        logging.warning("AlienVault OTX API key not configured. Skipping AlienVault OTX fetch.")

    # Fetch from AbuseIPDB
    if ABUSEIPDB_API_KEY and ABUSEIPDB_API_KEY != '5489b1d7dd9346cae4ffc0eb4c64a43dba74678d2a667ea2181c088fa489da5d891a8e81a1ec1222':
        logging.info("Fetching from AbuseIPDB...")
        # For AbuseIPDB, we provide a list of IPs to check.
        # In a real scenario, these IPs might come from other feeds or internal systems.
        # For this demo, we use a small hardcoded list of example IPs.
        example_ips_to_check = ["1.1.1.1", "8.8.8.8", "185.192.126.111", "192.168.1.1"] # Add/remove as needed
        abuseipdb_stix = abuseipdb_fetcher.fetch_recent_indicators(ip_list=example_ips_to_check)
        all_stix_objects.extend(abuseipdb_stix)
        logging.info(f"Collected {len(abuseipdb_stix)} STIX objects from AbuseIPDB.")
    else:
        logging.warning("AbuseIPDB API key not configured. Skipping AbuseIPDB fetch.")

    if all_stix_objects:
        logging.info(f"Total STIX objects collected: {len(all_stix_objects)}. Publishing to OpenTAXII...")
        stix_bundle = Bundle(all_stix_objects, allow_custom=True) # allow_custom for TLP_WHITE and custom properties
        success = taxii_publisher.publish_bundle(stix_bundle)
        if success:
            logging.info("STIX bundle successfully published to OpenTAXII.")
        else:
            logging.error("Failed to publish STIX bundle to OpenTAXII.")
    else:
        logging.info("No new STIX objects collected to publish.")

    logging.info("CTI collection and publishing cycle finished.")

if __name__ == "__main__":
    # This loop will make the container run continuously and fetch periodically
    # In a production environment, you might use a proper scheduler like Cron or Kubernetes cron jobs.
    while True:
        run_collection_and_publishing()
        # Wait for an hour before the next cycle
        logging.info("Waiting for 3600 seconds (1 hour) before next collection cycle...")
        time.sleep(3600)
