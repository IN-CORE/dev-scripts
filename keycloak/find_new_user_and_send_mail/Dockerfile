# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make your script executable
RUN chmod +x find_new_users_and_mail.py

# Run the Python script
CMD ["python", "./find_new_users_and_mail.py"]
