# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app/data_collection

# Add the current directory contents into the container at /app
ADD . /app/data_collection/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install webdriver_manager
RUN pip install webdriver_manager

# Install Firefox
RUN apt-get update && \
    apt-get install -y --no-install-recommends firefox-esr && \
    rm -rf /var/lib/apt/lists/*



# Make port 80 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "data_collection.py"]

