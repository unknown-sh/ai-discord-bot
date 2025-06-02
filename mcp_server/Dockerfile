FROM python:3.13.3-slim
ENV PYTHONPATH=/app
WORKDIR /app
# Copy mcp_server code
COPY mcp_server /app/mcp_server
# Copy shared dependencies
COPY ai_gateway /app/ai_gateway
COPY common /app/common
COPY config_engine /app/config_engine
# Install requirements for mcp_server
RUN pip install --no-cache-dir -r mcp_server/requirements.txt
EXPOSE 8001
CMD ["uvicorn", "mcp_server.main:app", "--host", "0.0.0.0", "--port", "8001"]
