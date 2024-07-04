FROM python:3.9-slim

#Installing c++ dependecy for vector db
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*


# Create and set the working directory
WORKDIR /app

# Copy only the requirements file first to leverage Docker caching
COPY flask_app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Expose the port your application will run on
EXPOSE 8080

# Specify the command to run on container start
CMD ["python", "flask_app/run.py"]
