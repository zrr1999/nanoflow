from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, Generic, ParamSpec, overload

from pydantic import BaseModel

P = ParamSpec("P")


class Workflow(BaseModel, Generic[P]):
    name: str
    fn: Callable[P, Coroutine[Any, Any, None]]

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        await self.fn(*args, **kwargs)

    def run(self, *args: P.args, **kwargs: P.kwargs) -> None:
        asyncio.run(self.fn(*args, **kwargs))


@overload
def workflow(fn: Callable[P, Coroutine[Any, Any, None]]) -> Workflow[P]: ...


@overload
def workflow(*, name: str | None = ...) -> Callable[[Callable[P, Coroutine[Any, Any, None]]], Workflow[P]]: ...


def workflow(
    fn: Callable[P, Coroutine[Any, Any, None]] | None = None, *, name: str | None = None
) -> Callable[[Callable[P, Coroutine[Any, Any, None]]], Workflow[P]] | Workflow[P]:
    def decorator(fn: Callable[P, Coroutine[Any, Any, None]]) -> Workflow[P]:
        return Workflow(name=name or fn.__name__, fn=fn)

    if fn is None:
        return decorator
    return decorator(fn)
