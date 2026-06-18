# Use a lightweight Python image as the base image
FROM python:3.12-slim

# Set the working directory inside the Docker container
WORKDIR /app

# Install system fonts needed for text rendering with Pillow
# --no-install-recommends keeps the image smaller
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency and package configuration files first
# This helps Docker cache the dependency installation step
COPY requirements.txt pyproject.toml ./

# Copy the source code into the container
COPY src ./src

# Copy the main entry file
COPY main.py ./

# Upgrade pip, install project dependencies, then install the project locally
# pip install -e . makes the ig_bild command available inside the container
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e .

# Default command when the container starts
# The helper script can pass extra arguments to this command
CMD ["ig_bild"]