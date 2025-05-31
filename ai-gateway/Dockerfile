FROM python:3.11-slim

# Set environment variables to avoid writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory inside container
WORKDIR /app

# Copy only requirements file first to leverage Docker cache
COPY ai-gateway/requirements.txt .

# Upgrade pip separately for better caching
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r ./requirements.txt

# Copy the rest of the ai-gateway app code
COPY ai-gateway/ ./ai_gateway/

# Copy sibling config-engine directory into /app/config_engine
COPY config-engine /app/config_engine

# Expose port 8000 for Uvicorn
EXPOSE 8000

# Start the FastAPI application using Uvicorn with module path
CMD ["python3", "-m", "uvicorn", "ai_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]