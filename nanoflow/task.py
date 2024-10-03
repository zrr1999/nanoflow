from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any, Generic, ParamSpec, TypeVar, overload

from loguru import logger
from pydantic import BaseModel, ConfigDict

from .resource_pool import ResourcePool

P = ParamSpec("P")
R = TypeVar("R")


class TaskProcessError(Exception):
    """Exception raised when a task process fails."""


class Task(BaseModel, Generic[P, R]):
    """
    Task to be executed by the workflow.

    Example:
    >>> my_task = Task(name="my_task", fn=lambda: print("Hello, world!"))
    >>> my_task()
    Hello, world!
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    fn: Callable[P, R]
    retry_interval: list[int] = [10, 30, 60]
    resource_pool: ResourcePool[Any] | None = None
    resource_modifier: Callable[[Callable[P, R], Any], Callable[P, R]] | None = None

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.fn(*args, **kwargs)

    def submit(self, *args: P.args, **kwargs: P.kwargs) -> asyncio.Task[R]:
        retry_interval = self.retry_interval[:]

        async def wrapper_fn():
            try:
                if self.resource_pool is not None:
                    resource = await self.resource_pool.acquire()
                    logger.info(f"Acquired resource: {resource}")
                    if self.resource_modifier is not None:
                        fn = self.resource_modifier(self.fn, resource)
                    else:
                        fn = self.fn
                    try:
                        return await asyncio.to_thread(fn, *args, **kwargs)
                    finally:
                        self.resource_pool.release(resource)
                        logger.info(f"Released resource: {resource}")
                else:
                    return await asyncio.to_thread(self.fn, *args, **kwargs)
            except TaskProcessError as e:
                logger.error(f"Failed to execute task: {e}")
                if retry_interval:
                    retry = retry_interval.pop(0)
                    logger.info(f"Retry task after {retry} seconds")
                    await asyncio.sleep(retry)
                    return await wrapper_fn()
                raise e

        return asyncio.create_task(wrapper_fn())


@overload
def task(fn: Callable[P, R]) -> Task[P, R]: ...


@overload
def task(
    *,
    name: str | None = None,
    resource_pool: ResourcePool[Any] | None = ...,
    resource_modifier: Callable[[Callable[P, R], Any], Callable[P, R]] | None = None,
) -> Callable[[Callable[P, R]], Task[P, R]]: ...


def task(
    fn: Callable[P, R] | None = None,
    *,
    name: str | None = None,
    resource_pool: ResourcePool[Any] | None = None,
    resource_modifier: Callable[[Callable[P, R], Any], Callable[P, R]] | None = None,
) -> Callable[[Callable[P, R]], Task[P, R]] | Task[P, R]:
    """Decorator to create a task.

    Example:
    >>> @task
    >>> def my_task(a: int, b: int) -> int:
    >>>     return a + b
    >>> my_task.name
    'my_task'
    >>> @task(name="custom_name")
    >>> def my_task(a: int, b: int) -> int:
    >>>     return a + b
    >>> my_task.name
    'custom_name'
    """

    def decorator(fn: Callable[P, R]) -> Task[P, R]:
        return Task(
            name=name or getattr(fn, "__name__", "unnamed"),
            fn=fn,
            resource_pool=resource_pool,
            resource_modifier=resource_modifier,
        )

    if fn is None:
        return decorator
    return decorator(fn)
