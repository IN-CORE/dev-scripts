# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY server/requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the application files (never the whole directory, which may hold
# a local .env or other secrets). Config comes from env vars at runtime.
COPY server/app.py server/incoreuser.py server/newemail.py ./
COPY server/templates/*.html ./templates/

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port that the app runs on
EXPOSE 5000

# Run the Flask application
CMD ["flask", "run"]
