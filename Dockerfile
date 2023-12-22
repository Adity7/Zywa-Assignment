# Use the official Python image as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose the port that Gunicorn will run on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=fetch.py
ENV FLASK_RUN_HOST=0.0.0.0

# Use Gunicorn to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "fetch:app"]
