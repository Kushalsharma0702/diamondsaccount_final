FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules first
COPY shared/ ./shared/

# Copy service code
COPY services/gateway/ ./services/gateway/

# Expose port
EXPOSE 8000

# Run the service
CMD ["python", "services/gateway/main.py"]
