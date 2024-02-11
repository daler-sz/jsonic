from dataclasses import dataclass
from typing import Any, Protocol


class SyncMethodByName(Protocol):
    def __call__(self, *args, **kwargs) -> Any:
        ...


class SyncMethodByPosition(Protocol):
    def __call__(self, *args) -> Any:
        ...


class AsyncMethodByName(Protocol):
    async def __call__(self, *args, **kwargs) -> Any:
        ...


class AsyncMethodByPosition(Protocol):
    async def __call__(self, *args) -> Any:
        ...


SyncMethod = SyncMethodByName | SyncMethodByPosition
AsyncMethod = AsyncMethodByName | AsyncMethodByPosition

Method = SyncMethod | AsyncMethod


@dataclass(frozen=True, kw_only=True)
class BaseRegisteredMethod:
    name: str
    is_by_position: bool
    origin: Method
    allow_notifications: bool = True
    allow_requests: bool = True

    def __call__(self, *args, **kwargs):
        return self.origin(*args, **kwargs)


@dataclass(frozen=True)
class SyncRegisteredMethod(BaseRegisteredMethod):
    origin: SyncMethod

    def __call__(self, *args, **kwargs):
        return self.origin(*args, **kwargs)


@dataclass(frozen=True)
class AsyncRegisteredMethod(BaseRegisteredMethod):
    origin: AsyncMethod

    async def __call__(self, *args, **kwargs):
        return await self.origin(*args, **kwargs)


RegisteredMethod = SyncRegisteredMethod | AsyncRegisteredMethod
