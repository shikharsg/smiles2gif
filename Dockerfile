# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Install system dependencies required for RDKit and Cairo
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements and install Python dependencies using uv
COPY requirements.txt .
RUN uv pip install --no-cache --system -r requirements.txt

# Copy the application code
COPY app.py .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.address", "127.0.0.1"]
