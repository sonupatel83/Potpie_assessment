# Use Python base image
FROM python:3.8-slim

# Set working directory in the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install system dependencies for PostgreSQL and curl for healthchecks
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
