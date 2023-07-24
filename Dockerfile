# syntax=docker/dockerfile:1

# Use the official Python base image
FROM python:3.9-slim
LABEL maintainer="oloruntoba.olasubomi@gmail.com"
ENV TZ America/Phoenix

WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code to the container
COPY . .

# Expose the port on which the Flask app will run
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=submit.py

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]



