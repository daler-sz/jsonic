from abc import ABC, abstractmethod
from typing import Annotated, Any, Generic, TypeVar

from jsonic_rpc._internal.abstractions.method import (
    AsyncRegisteredMethod,
    SyncRegisteredMethod,
)
from jsonic_rpc._internal.abstractions.serializing import BaseLoader
from jsonic_rpc._internal.types import Params, Result


class Depends:
    def __init__(self, param: Any = None):
        self.param = param


T = TypeVar("T")
Context = TypeVar("Context")
Dependency = Annotated[T, Depends()]


class BaseDiInjector(ABC, Generic[Context]):
    @abstractmethod
    def call_injected(
        self,
        method: SyncRegisteredMethod,
        loader: BaseLoader,
        params: Params,
        context: Context | None,
    ) -> Result:
        ...

    @abstractmethod
    async def async_call_injected(
        self,
        method: AsyncRegisteredMethod,
        loader: BaseLoader,
        params: Params,
        context: Context | None,
    ) -> Result:
        ...
