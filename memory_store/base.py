"""
Abstract base class for memory store implementations.
"""

import abc
from typing import Any, List, Optional


class BaseMemoryStore(abc.ABC):
    @abc.abstractmethod
    async def set(self, user_id: str, key: str, value: Any) -> str:
        pass

    @abc.abstractmethod
    async def get(self, user_id: str, key: str) -> Optional[Any]:
        pass

    @abc.abstractmethod
    async def update(self, user_id: str, key: str, value: Any) -> bool:
        pass

    @abc.abstractmethod
    async def delete(self, user_id: str, key: str) -> bool:
        pass

    @abc.abstractmethod
    async def list(self, user_id: str) -> List[Any]:
        pass
