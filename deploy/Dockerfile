FROM python:3.11-slim

# Set environment variables to prevent Python from creating .pyc files
# and enable unbuffered output for better logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

COPY requirements.txt ./ai-gateway/

# Upgrade pip separately to improve caching and stability
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r ai-gateway/requirements.txt

# Copy the rest of the application source code
COPY ai-gateway ./ai-gateway
COPY config-engine ./config-engine
COPY common ./common

# Expose port 8000 for Uvicorn server
EXPOSE 8000

# Run the FastAPI app using uvicorn with host 0.0.0.0 to listen on all interfaces
CMD ["python3", "-m", "uvicorn", "ai_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Note:
# - Ensure your build context includes all necessary files (e.g., config-engine) if your project depends on them.
# - Consider adding a .dockerignore file (if not present) to exclude files/folders like __pycache__, .git, etc., to improve build performance and keep the image lean.
