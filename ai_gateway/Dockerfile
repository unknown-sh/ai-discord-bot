

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPATH=/app:/app/mcp_server:/app/common:/app/config_engine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for dependency installation
COPY ai_gateway/requirements.txt .
COPY ai_gateway/setup.py .

# Copy the ai_gateway directory as a subdirectory
COPY ai_gateway /app/ai_gateway

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Copy other necessary directories
COPY mcp_server/ /app/mcp_server/
COPY common/ /app/common/
COPY config_engine/ /app/config_engine/

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Diagnostic: List /app and /app/ai_gateway contents
RUN ls -l /app && ls -l /app/ai_gateway

# Command to run the application
CMD ["uvicorn", "ai_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]