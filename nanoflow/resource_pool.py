from __future__ import annotations

import asyncio
from typing import Generic, TypeVar

T = TypeVar("T")


class ResourcePool(Generic[T]):
    def __init__(self, resources: list[T]):
        self.resources = {res: asyncio.Semaphore(1) for res in resources}

    async def acquire(self) -> T:
        while True:
            for res, sem in self.resources.items():
                if sem.locked():
                    continue
                if await sem.acquire():
                    return res
            await asyncio.sleep(0.1)

    def release(self, res: T):
        self.resources[res].release()
