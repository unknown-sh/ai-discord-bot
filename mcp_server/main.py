from fastapi import FastAPI
from mcp_server import router

app = FastAPI()
app.include_router(router.router)
