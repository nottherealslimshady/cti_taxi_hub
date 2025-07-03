# config.py
# Centralized configuration for API keys and OpenTAXII details

import os

# OpenTAXII Server Configuration
OPENTAXII_SERVER_URL = os.getenv('OPENTAXII_SERVER_URL', 'http://localhost:9000')
OPENTAXII_COLLECTION_ID = os.getenv('OPENTAXII_COLLECTION_ID', 'default_collection') # OpenTAXII's default collection
OPENTAXII_USERNAME = os.getenv('OPENTAXII_USERNAME', 'admin')
OPENTAXII_PASSWORD = os.getenv('OPENTAXII_PASSWORD', 'YvhzY3gGHHbpfNvXa0c-RpuqYnRxLRFm11QAwDOEQ-Y3b_MGLGLVWwsmpC7LKfEG6hOwFOcL9P4ZfutiwM7ZiA') # Must match docker-compose.yml

# CTI Feed API Keys (Get these from your respective accounts)
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY', '513bf61cf011c015a0a5124ae7aa140412381e6b2115907fcfc500547e573fa2') # Free tier available
ALIENVAULT_OTX_API_KEY = os.getenv('ALIENVAULT_OTX_API_KEY', 'cc10d2976dbe84523c003c2b0b3bdb9ba375683d1b3469aec36438aa2c98acec') # Free tier available
ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY', '5489b1d7dd9346cae4ffc0eb4c64a43dba74678d2a667ea2181c088fa489da5d891a8e81a1ec1222') # Free tier available (requires registration)
