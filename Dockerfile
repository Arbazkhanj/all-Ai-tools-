FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create models directory
RUN mkdir -p /root/.u2net

# Expose port
EXPOSE 7860

# Run the server
CMD ["rembg", "s", "--host", "0.0.0.0", "--port", "7860", "--log_level", "info"]
