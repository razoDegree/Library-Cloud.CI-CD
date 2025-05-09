# Use an official lightweight Python image as the base
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port your app will run on (Flask default is 5000)
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
