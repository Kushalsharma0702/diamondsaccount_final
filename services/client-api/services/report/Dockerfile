FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF generation
RUN apt-get update && apt-get install -y \
    gcc \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules first
COPY shared/ ./shared/

# Copy service code
COPY services/report/ ./services/report/

# Expose port
EXPOSE 8004

# Run the service
CMD ["python", "services/report/main.py"]
