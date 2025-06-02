# AI Discord Bot Deployment

This directory contains Docker and Compose configuration for deploying the AI Discord Bot system, including the FastAPI AI Gateway and Discord client.

## Prerequisites
- Docker and Docker Compose installed
- API keys and configuration values in a `.env` file (see below)

## Quick Start

1. **Clone the repository** and navigate to the project root.
2. **Create a `.env` file** in the `deploy` directory with the required environment variables (see below).
3. **Build and start the stack:**
   ```sh
   docker compose up --build
   ```
4. The FastAPI gateway will be available at `http://localhost:8000`.

## Environment Variables
Set these in your `.env` file in the `deploy` directory:

```
# Discord
DISCORD_TOKEN=your-discord-bot-token

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-key

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# AI Provider
AI_PROVIDER=openai
AI_PERSONALITY=default

# Logging
LOG_FILE=bot_actions.log
```

## Healthchecks
- The `ai-gateway` service exposes `/healthz` for Docker healthcheck integration.
- Docker Compose will restart the service if it becomes unhealthy.

## Updating and Troubleshooting
- To rebuild after code changes:
  ```sh
  docker compose up --build
  ```
- Logs can be viewed with:
  ```sh
  docker compose logs -f
  ```
- If you change dependencies, ensure `requirements.txt` is up to date.

## Volumes and Hot Reload
- The Compose file mounts source directories for live reload in development.
- For production, consider removing volumes and building a static image.

## Adding More Services
- Add new services to `docker-compose.yml` as needed.
- Use the shared network for inter-service communication.

---

For more details or troubleshooting, see the comments in `docker-compose.yml` and `Dockerfile`.
