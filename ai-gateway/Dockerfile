FROM python:3.11-slim

# Set environment variables to avoid writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory inside container
WORKDIR /app

COPY requirements.txt .

# Upgrade pip separately for better caching
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ai-gateway/ ./ai_gateway/


# Expose port 8000 for Uvicorn
EXPOSE 8000

# Start the FastAPI application using Uvicorn with module path
CMD ["uvicorn", "ai_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]