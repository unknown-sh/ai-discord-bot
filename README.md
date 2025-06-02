# AI Discord Bot System

A secure, extensible, and natural-language-enabled Discord bot platform with:
- LLM-based command routing
- Role-based access control
- Supabase integration
- FastAPI backend
- Dockerized deployment
- Optional web dashboard for management

## Features
- **Natural Language Commands**: Use GPT-4 or other LLMs to route and interpret Discord commands, including role management, configuration, and audit log queries.
- **Role-Based Access Control**: Only users with the correct roles (admin/superadmin) can perform sensitive actions.
- **Audit Logging**: All sensitive actions are logged and can be retrieved by superadmins.
- **Config Management**: Securely set and get canonical config keys (e.g., `OPENAI_MODEL`, `AI_PROVIDER`, `AI_PERSONALITY`).
- **Supabase Backend**: Roles, audit logs, and config are stored in Supabase.
- **FastAPI Gateway**: Python backend for API endpoints and LLM integration.
- **Docker Compose Deployment**: Easily run the full stack locally or in production.
- **Web Dashboard**: (Optional) React dashboard for bot management and analytics.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- API keys: Discord, OpenAI (or other LLM), Supabase

### 1. Clone the Repository
```sh
git clone <this-repo>
cd ai-discord-bot
```

### 2. Configure Environment
Create a `.env` file in `deploy/`:
```env
DISCORD_TOKEN=your-discord-bot-token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-key
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
AI_PROVIDER=openai
AI_PERSONALITY=default
LOG_FILE=bot_actions.log
```

### 3. Build and Run
```sh
cd deploy
docker compose up --build
```
- FastAPI gateway: [http://localhost:8000](http://localhost:8000)
- Discord bot: will log in automatically

### 4. Web Dashboard (Optional)
```sh
cd web-dashboard
npm install
npm start
```
- Dashboard: [http://localhost:3000](http://localhost:3000)

## Advanced Usage
- **Hot reload**: Source directories are mounted for live reload in dev.
- **Production**: Remove volumes and build static images.
- **Logs**: `docker compose logs -f` or check `LOG_FILE`.
- **Healthchecks**: `/healthz` endpoint for gateway.

## Integrating with External Agents (Claude Desktop, etc.)
- You can connect external MCP-compatible agents (like Claude Desktop) to your MCP server.
- Add a config block to your Claude Desktop config (see their docs) to point at your running MCP server.
- Claude Desktop and other agents are external processes; there is no fully embedded agent with MCP+LLM out of the box as of June 2025.

## Security & Best Practices
- Only canonical config keys are allowed.
- Sensitive values (API keys, secrets) are never exposed in outputs.
- All permission checks are enforced both in the client and backend.
- Fallbacks and error messages are user-friendly and actionable.

## Project Structure
- `discord-client/` — Node.js Discord bot & LLM router
- `mcp_server/` — FastAPI backend (Python)
- `web-dashboard/` — (Optional) React dashboard
- `deploy/` — Docker Compose configs and deployment scripts

## Extending & Customizing
- Add new MCP endpoints in `mcp_server/router.py`
- Extend NL command routing in `discord-client/llm_router.js`
- Add more role types or config keys as needed

## References
- [Supabase](https://supabase.com/)
- [Discord API](https://discord.com/developers/docs/intro)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Smithery](https://smithery.ai/) (for MCP agent discovery)

---

**Note:**
- There is currently no fully embedded local LLM+MCP agent SDK. All AI agents (Claude Desktop, etc.) must run as separate processes and connect via MCP.
- For local LLMs, use open-source models with compatible MCP wrappers or integrate directly in your backend.
