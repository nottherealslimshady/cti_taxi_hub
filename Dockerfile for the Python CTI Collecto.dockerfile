# Dockerfile for the Python CTI Collector/Publisher application

# Use the official Python image as a base
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any, though not strictly needed for basic Python)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . .

# Command to run the application (overridden by docker-compose.yml)
# CMD ["python3", "main.py"]
