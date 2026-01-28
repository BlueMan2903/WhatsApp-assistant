# Dockerfile

# 1. Use an official Python runtime as a parent image
# Using python:3.13-slim to match your development environment while keeping the image small
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy and install the dependencies
# This is done first to leverage Docker's layer caching for faster builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your application's code into the container
# This includes app.py, the 'assistant/' package, 'contexts/', etc.
COPY . .

# 5. Expose the port that Gunicorn will run on
EXPOSE 5000

# 6. Define the command to run the app using the Gunicorn server
# Binds the server to all network interfaces on port 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]