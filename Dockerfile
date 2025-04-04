# Use official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Flask app into the container
COPY . .

# Set the environment variable to indicate that we are running in production
ENV FLASK_ENV=production

# Expose the port that Flask will run on (by default 5000)
EXPOSE 80

# Command to run the application
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:80"]