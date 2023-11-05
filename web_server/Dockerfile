# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /web_server
WORKDIR /app/web_server

# Add the current directory contents into the container at /web_server
ADD . /app/web_server/




USER root
RUN apt-get update && apt-get install -y \
    pkg-config \
    python3-dev \
    libcairo2-dev \
    libsystemd-dev \
    libgirepository1.0-dev \
    gir1.2-gtk-3.0




# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run server.py when the container launches
CMD ["python", "server.py"]
