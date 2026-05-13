# Use a lightweight Python base image
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files 
# and to ensure output is sent straight to terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# - exiftool: The primary engine for metadata removal
# - libimage-exiftool-perl: The package name for exiftool on debian/ubuntu
RUN apt-get update && apt-get install -y --no-install-recommends \
    exiftool \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Install Python libraries
# We install 'rich' for the UI and 'pikepdf' for PDF cleaning
RUN pip install --no-cache-dir rich pikepdf

# Copy the script into the container
COPY metadata_stripper.py .

# Create a 'data' directory where users can mount their files
RUN mkdir /data

# Run as a non-privileged user for better security
RUN useradd -m appuser && chown -R appuser:appuser /app /data
USER appuser

# Set the entrypoint to run the script
# We point it to the /data directory by default
ENTRYPOINT ["python", "metadata_stripper.py"]