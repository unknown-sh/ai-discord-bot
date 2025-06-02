import pytest
import pytest_asyncio
from ai_gateway.main import app
from httpx import AsyncClient


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_help_root(async_client):
    resp = await async_client.get(
        "/help",
        headers={"x-discord-user-id": "testuser", "x-discord-username": "tester"},
    )
    assert resp.status_code == 200
    assert "Bot Help" in resp.json().get("text", "")


from unittest.mock import patch, AsyncMock
import types

async def noop_log_audit_event(*args, **kwargs):
    return None

@pytest.mark.asyncio
async def test_show_config(async_client):
    import ai_gateway.routers.config as config_router
    with patch("ai_gateway.decorators.get_user_role", new=AsyncMock(return_value="admin")), \
         patch.object(config_router, "log_audit_event", new=noop_log_audit_event):
        resp = await async_client.get(
            "/show/config",
            headers={"x-discord-user-id": "admin", "x-discord-username": "adminuser"},
        )
        assert resp.status_code == 200
        assert "config" in resp.json().get("text", "")


@pytest.mark.asyncio
async def test_help_root(async_client):
    resp = await async_client.get(
        "/help",
        headers={"x-discord-user-id": "testuser", "x-discord-username": "tester"},
    )
    assert resp.status_code == 200
    assert "Bot Help" in resp.json().get("text", "")


import pytest
import pytest_asyncio
from ai_gateway.main import app
from httpx import AsyncClient
from unittest.mock import patch

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_ask_endpoint(async_client):
    import ai_gateway.routers.ask as ask_router
    with patch("ai_gateway.decorators.get_user_role", new=AsyncMock(return_value="user")), \
         patch.object(ask_router, "log_audit_event", new=noop_log_audit_event):
        resp = await async_client.post(
            "/ask",
            json={"message": "Hello!"},
            headers={"x-discord-user-id": "testuser", "x-discord-username": "tester"},
        )
        assert resp.status_code == 200
        assert "reply" in resp.json()


