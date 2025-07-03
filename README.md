# cti_taxi_hub

Cloud-Based Open Source CTI TAXII Hub
This project demonstrates the creation of a robust, cloud-based open-source Cyber Threat Intelligence (CTI) pipeline. It leverages Docker and AWS to deploy a self-hosted TAXII 1.x server (OpenTAXII) and a Python application that collects CTI from various public sources, transforms it into the standardized STIX 2.x format, and publishes it to the OpenTAXII server.

This setup provides a centralized, standardized, and accessible source of open-source threat intelligence, showcasing key skills in cloud deployment, containerization, API integration, and CTI data standardization.

Features
Dockerized Deployment: All components (database, TAXII server, CTI collector) run in Docker containers, ensuring portability and consistent environments.

AWS EC2 Hosting: Instructions for deploying the entire stack on an Amazon Web Services (AWS) EC2 instance.

OpenTAXII Server: A self-hosted TAXII 1.x server for receiving and serving STIX-formatted threat intelligence.

Open Source CTI Integration:

VirusTotal: Fetches indicators (IPs, domains, URLs, file hashes) and converts them to STIX.

AlienVault OTX: Fetches "pulses" and extracts indicators, converting them to STIX.

(Optional: Spamhaus - requires API key, not fully implemented in default code due to common licensing restrictions on free tiers)

STIX 2.x Standardization: All collected intelligence is transformed into STIX 2.x format, a widely accepted standard for cyber threat information.

Automated Publishing: A Python script periodically fetches new intelligence and publishes it to the OpenTAXII server's inbox.

Project Structure
.
├── docker-compose.yml          # Defines Docker services (DB, OpenTAXII, CTI Collector)
├── Dockerfile                  # Builds the Python CTI Collector image
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration for API keys and OpenTAXII
├── vt_fetcher.py               # Fetches data from VirusTotal
├── otx_fetcher.py              # Fetches data from AlienVault OTX
├── taxii_publisher.py          # Converts to STIX and publishes to OpenTAXII
└── main.py                     # Orchestrates the fetching and publishing process

Prerequisites
AWS Account: With permissions to launch EC2 instances and configure security groups.

Docker & Docker Compose: Installed on your local machine (for development/testing) and on the AWS EC2 instance.

Python 3.x: (For local development/understanding scripts).

API Keys:

VirusTotal: A free API key (available after registration on VirusTotal).

AlienVault OTX: A free API key (available after registration on AlienVault OTX).

(Optional) Spamhaus: If you have access to a Spamhaus API, you can extend the project.

Setup and Deployment
Follow these steps to get your CTI TAXII Hub running on AWS.

1. Local Project Setup

Clone/Create Project Directory:

mkdir cti-taxii-hub
cd cti-taxii-hub

Create Files: Place the docker-compose.yml, Dockerfile, requirements.txt, config.py, vt_fetcher.py, otx_fetcher.py, taxii_publisher.py, and main.py files into this directory.

Configure API Keys and Passwords:

Open docker-compose.yml and replace placeholder values:

your_strong_db_password

your_opentaxii_auth_secret

your_opentaxii_admin_password

Open config.py and replace placeholder values:

YOUR_VIRUSTOTAL_API_KEY

YOUR_ALIENVAULT_OTX_API_KEY

Ensure OPENTAXII_PASSWORD matches the one set in docker-compose.yml.

2. Deploy to AWS EC2

Follow the detailed instructions in the AWS EC2 Deployment Guide to:

Launch an EC2 instance (e.g., Ubuntu 20.04 LTS, t2.micro).

Configure a Security Group to allow SSH (port 22) and OpenTAXII HTTP (port 9000).

Connect to your EC2 instance via SSH.

Install Docker and Docker Compose on the EC2 instance.

Copy your project files to the EC2 instance (e.g., using scp or by creating them directly).

Navigate to your project directory on the EC2 instance and run:

docker-compose up --build -d

3. Verification

Check Container Status:

docker-compose ps

All services (db, opentaxii, cti_collector) should be in the Up state.

Monitor Collector Logs:

docker-compose logs -f cti_collector

You will see logs indicating the fetching process from VirusTotal and AlienVault OTX, and the publishing attempts to OpenTAXII.

Access OpenTAXII Discovery Service:

Open your web browser and navigate to http://<YOUR_EC2_PUBLIC_IP>:9000/services/discovery.

You should see an XML response confirming the OpenTAXII server is running.

Access OpenTAXII Collection Management:

Navigate to http://<YOUR_EC2_PUBLIC_IP>:9000/services/collection-management.

You might be prompted for credentials. Use the admin username and your_opentaxii_admin_password you configured. You should see a list of collections, including default_collection.

How it Works
OpenTAXII & PostgreSQL: The docker-compose.yml sets up OpenTAXII as a TAXII 1.x server, backed by a PostgreSQL database for persistent storage of CTI data.

CTI Collector (cti_collector service):

This is a Python application running in its own Docker container.

It uses vt_fetcher.py and otx_fetcher.py to make API calls to VirusTotal and AlienVault OTX, respectively.

The fetched raw intelligence is parsed and converted into STIX 2.x Indicator and Observable objects using the stix2 Python library.

The taxii_publisher.py then takes these STIX objects, bundles them, and sends them to the OpenTAXII server's Inbox service using HTTP POST requests with a TAXII 1.x XML wrapper.

The main.py script orchestrates this process, running it periodically (e.g., every hour).

Data Flow:
VirusTotal / OTX APIs -> Python Fetchers -> STIX 2.x Conversion -> TAXII Publisher -> OpenTAXII Inbox -> OpenTAXII Database

Troubleshooting
Containers not starting: Check docker-compose logs <service_name> for errors.

API Key Issues: Double-check your API keys in config.py and ensure they are correctly set as environment variables in docker-compose.yml.

Rate Limits: Free tier APIs (like VirusTotal, OTX) have rate limits. The Python scripts include basic time.sleep() for 429 errors, but you might hit limits if you try to fetch too much too quickly.

Security Group: Ensure port 9000 (and 22 for SSH) is open in your AWS EC2 Security Group.

OpenTAXII Authentication: If you can't access collection management, verify the OPENTAXII_ADMIN_USER and OPENTAXII_ADMIN_PASS in docker-compose.yml.

Next Steps / Enhancements
Error Handling and Robustness: Implement more sophisticated error handling, retry mechanisms, and dead-letter queues for failed API calls or STIX conversions.

Advanced STIX Mapping: Map more complex attributes from CTI feeds (e.g., malware families, threat actors, TTPs) to richer STIX objects.

Deduplication Logic: Implement logic to prevent publishing duplicate indicators to OpenTAXII if they already exist.

Configuration Management: Use a proper configuration management tool (e.g., Ansible) for deploying to AWS.

Monitoring: Add monitoring for container health and application logs.

More Feeds: Integrate additional open-source CTI feeds (e.g., Abuse.ch, MISP instances, public government feeds).

TAXII 2.x: Explore setting up a TAXII 2.x server (e.g., cti-taxii-server) and using python-taxii2 for publishing, as TAXII 2.x is the more modern standard.

This project provides a solid foundation for understanding the technical aspects of CTI integration and will be a strong demonstration of your capabilities.
