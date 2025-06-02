#!/bin/bash
set -e

# Refactored build script for AI Discord Bot full stack
# Usage: ./build.sh [--run-after-build]

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Ensure and activate Python virtual environment
if [ ! -d ".venv" ]; then
    echo "Python virtual environment (.venv) not found. Creating one..."
    python3 -m venv .venv
fi

echo "Activating Python virtual environment..."
source .venv/bin/activate

RUN_AFTER_BUILD=false
for arg in "$@"; do
    case $arg in
        --run-after-build)
            RUN_AFTER_BUILD=true
            ;;
    esac
done

# 0. Clean previous builds and caches
echo "[0/4] Cleaning previous builds and caches..."
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name ".pytest_cache" -type d -exec rm -rf {} +

# 1. Install Python dependencies
echo "[1/4] Installing Python dependencies..."
# Install root requirements.txt if present
if [ -f "requirements.txt" ]; then
    echo "Installing root Python dependencies..."
    pip install --upgrade pip
    pip install --no-cache-dir -r requirements.txt
fi
# Install ai_gateway dependencies
if [ -d "ai_gateway" ] && [ -f "ai_gateway/requirements.txt" ]; then
    echo "Installing ai_gateway dependencies..."
    pip install --no-cache-dir -r ai_gateway/requirements.txt
fi
# Install mcp_server dependencies
if [ -d "mcp_server" ] && [ -f "mcp_server/requirements.txt" ]; then
    echo "Installing mcp_server dependencies..."
    pip install --no-cache-dir -r mcp_server/requirements.txt
fi

# 2. Build frontend (if Node.js is available)
if command -v npm &> /dev/null && [ -d "web-dashboard" ]; then
    echo "[2/4] Building frontend..."
    pushd web-dashboard > /dev/null
    echo "Installing Node.js dependencies..."
    npm install --prefer-online --no-audit --progress=false
    echo "Building frontend..."
    npm run build
    popd > /dev/null
else
    echo "[2/4] Skipping frontend build (npm not found or web-dashboard directory missing)"
fi

# 3. Docker build (using /deploy/docker-compose.yml)
echo "[3/4] Building and starting Docker containers (discord-client, ai-gateway, mcp-memory)..."
if command -v docker &> /dev/null; then
    echo "Stopping any running containers..."
    docker compose -f deploy/docker-compose.yml down 2>/dev/null || true

    # Create .env file if it doesn't exist
    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        echo "Creating .env file from .env.example..."
        cp .env.example .env
    fi

    echo "Building Docker containers (no cache, always fresh code)..."
    DOCKER_BUILDKIT=1 docker compose -f deploy/docker-compose.yml build --no-cache --progress=plain
    echo "[NOTE] If you want to force a totally clean build (including images), run: docker compose -f deploy/docker-compose.yml build --no-cache"
    echo "[INFO] This will build: discord-client, ai-gateway, and mcp-memory containers."

    # Check if build was successful
    if [ $? -eq 0 ]; then
        echo "Docker build completed successfully!"
        # Start containers if requested
        if [ "$RUN_AFTER_BUILD" = true ]; then
            echo "Starting all containers (including mcp-memory)..."
            docker compose -f deploy/docker-compose.yml up
        else
            echo -e "\nBuild complete! You can start the containers with:"
            echo "docker compose -f deploy/docker-compose.yml up"
        fi
    else
        echo "Error: Docker build failed. Please check the build output above for details."
        exit 1
    fi
else
    echo "Docker not found. Skipping container build and start."
    echo "You can install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi
