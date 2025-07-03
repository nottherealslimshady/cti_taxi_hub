# taxii_publisher.py
# Publishes STIX 2.x bundles to an OpenTAXII 1.x Inbox service

import requests
import json
from stix2 import Bundle # Added Bundle import
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TAXIIPublisher:
    def __init__(self, server_url, collection_id, username, password):
        self.server_url = server_url
        self.collection_id = collection_id
        self.username = username
        self.password = password
        self.inbox_url = f"{self.server_url}/services/inbox" # Default OpenTAXII Inbox path
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

    def publish_bundle(self, stix_bundle):
        """
        Publishes a STIX 2.x Bundle to the OpenTAXII Inbox service.
        OpenTAXII 1.x Inbox expects a TAXII Message (XML) containing STIX.
        For simplicity, we'll send the STIX bundle wrapped in a basic TAXII 1.x Content Block XML.
        """
        if not isinstance(stix_bundle, Bundle):
            stix_bundle = Bundle(stix_bundle) # Ensure it's a Bundle

        stix_json = stix_bundle.serialize(pretty=True)
        logging.info(f"Attempting to publish STIX bundle with {len(stix_bundle.objects)} objects.")

        # Construct a basic TAXII 1.x message for the Inbox service
        taxii_message = f"""<?xml version="1.0" encoding="UTF-8"?>
<taxii_10:Taxii_Message xmlns:taxii_10="http://taxii.mitre.org/messages/taxii_1.0/"
    xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1"
    xmlns:tdq="http://taxii.mitre.org/query/taxii_default_query_1.0/"
    xmlns:stix="http://stix.mitre.org/stix-1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    message_id="{int(time.time() * 1000)}"
    in_response_to="None">
    <taxii_10:Inbox_Message>
        <taxii_10:Destination_Collection_Name>{self.collection_id}</taxii_10:Destination_Collection_Name>
        <taxii_10:Content_Block>
            <taxii_10:Content_Binding binding_id="urn:stix.mitre.org:json:2.1"/>
            <taxii_10:Content>{stix_json}</taxii_10:Content>
        </taxii_10:Content_Block>
    </taxii_10:Inbox_Message>
</taxii_10:Taxii_Message>
"""
        headers = {
            "Content-Type": "application/xml", # TAXII 1.x typically expects XML
            "X-TAXII-Content-Type": "urn:taxii.mitre.org:message:xml:1.0",
            "X-TAXII-Accept": "urn:taxii.mitre.org:message:xml:1.0",
            "X-TAXII-Services": "urn:taxii.mitre.org:services:1.0"
        }

        try:
            response = self.session.post(self.inbox_url, data=taxii_message.encode('utf-8'), headers=headers)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            logging.info(f"Successfully published STIX bundle to OpenTAXII Inbox. Status: {response.status_code}")
            logging.debug(f"OpenTAXII Response: {response.text}")
            return True
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error publishing to OpenTAXII: {e.response.status_code} - {e.response.text}")
            return False
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error publishing to OpenTAXII: {e}")
            return False
