# Use the official Python image from DockerHub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire contents of the local directory to the working directory in the container
COPY . .

# Set environment variable to ensure Python output is sent to stdout/stderr
ENV PYTHONUNBUFFERED=1

# Run the r_read.py script
CMD ["python", "r_read.py"]
