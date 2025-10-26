from typing import Type
from aiogram_toolkit.dashboard.memory.base import BaseCluster, MemoryCluster
from fakeredis import FakeAsyncRedis

class MemoryProvider:
    """
    A customizable and unified interface for managing memory clusters and Redis client access.
    Provides a ready-to-use `cluster` via attribute or call.
    """
    def __init__(
        self,
        client=None,
        ctr_cls: Type[BaseCluster] = MemoryCluster,
    ):
        self._client = client
        self._ctr_cls = ctr_cls

    @property
    def cluster(self):
        return self._ctr_cls(redis_client=self.get_client())

    def get_client(self):
        """
        Return the active Redis client (external or default).
        """
        return self._client or FakeAsyncRedis()
