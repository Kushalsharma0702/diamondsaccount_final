FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for file processing
RUN apt-get update && apt-get install -y \
    gcc \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules first
COPY shared/ ./shared/

# Copy service code
COPY services/file/ ./services/file/

# Expose port
EXPOSE 8003

# Run the service
CMD ["python", "services/file/main.py"]
