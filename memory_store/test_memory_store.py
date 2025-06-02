import asyncio

import pytest
from memory_store.inmemory_store import InMemoryMemoryStore
from memory_store.supabase_store import SupabaseMemoryStore


@pytest.mark.asyncio
@pytest.mark.parametrize("store_cls", [InMemoryMemoryStore])
async def test_memory_store_crud(store_cls):
    store = store_cls()
    user_id = "testuser"
    key = "foo"
    value = {"bar": 42}

    # set
    mem_id = await store.set(user_id, key, value)
    assert mem_id

    # get
    got = await store.get(user_id, key)
    assert got == value

    # update
    updated = await store.update(user_id, key, {"bar": 99})
    assert updated
    got2 = await store.get(user_id, key)
    assert got2 == {"bar": 99}

    # list
    items = await store.list(user_id)
    assert any(item["key"] == key and item["value"] == {"bar": 99} for item in items)

    # delete
    deleted = await store.delete(user_id, key)
    assert deleted
    got3 = await store.get(user_id, key)
    assert got3 is None


@pytest.mark.asyncio
async def test_memory_store_isolation():
    store = InMemoryMemoryStore()
    await store.set("user1", "a", 1)
    await store.set("user2", "a", 2)
    val1 = await store.get("user1", "a")
    val2 = await store.get("user2", "a")
    assert val1 == 1
    assert val2 == 2
