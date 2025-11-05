# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Create a non-root user first
RUN useradd --create-home appuser

# Set the working directory and change its ownership
WORKDIR /app
RUN chown appuser:appuser /app

# Switch to the non-root user
USER appuser

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN python3 -m venv .venv
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PATH="/app/.venv/bin:$PATH"

# Run server.py when the container launches using shell form to pass the PORT env var
CMD fastmcp run server.py --host 0.0.0.0 --port $PORT
