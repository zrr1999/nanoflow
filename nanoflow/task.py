from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any, Generic, ParamSpec, TypeVar, overload

from pydantic import BaseModel, ConfigDict

from .resource_pool import ResourcePool

P = ParamSpec("P")
R = TypeVar("R")


class Task(BaseModel, Generic[P, R]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    fn: Callable[P, R]
    resource_pool: ResourcePool[Any] | None = None

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.fn(*args, **kwargs)

    def submit(self, *args: P.args, **kwargs: P.kwargs) -> asyncio.Task[R]:
        async def wrapper_fn():
            if self.resource_pool is not None:
                resource = await self.resource_pool.acquire()
                try:
                    return await asyncio.to_thread(self.fn, *args, **kwargs)
                finally:
                    self.resource_pool.release(resource)
            else:
                return await asyncio.to_thread(self.fn, *args, **kwargs)

        return asyncio.create_task(wrapper_fn())


@overload
def task(fn: Callable[P, R]) -> Task[P, R]: ...


@overload
def task(
    *,
    name: str | None = None,
    resource_pool: ResourcePool[Any] | None = ...,
) -> Callable[[Callable[P, R]], Task[P, R]]: ...


def task(
    fn: Callable[P, R] | None = None,
    *,
    name: str | None = None,
    resource_pool: ResourcePool[Any] | None = None,
) -> Callable[[Callable[P, R]], Task[P, R]] | Task[P, R]:
    def decorator(fn: Callable[P, R]) -> Task[P, R]:
        return Task(name=name or getattr(fn, "__name__", "unnamed"), fn=fn, resource_pool=resource_pool)

    if fn is None:
        return decorator
    return decorator(fn)
