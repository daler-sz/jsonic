from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from jsonic_rpc._internal.abstractions.method import (
    AsyncRegisteredMethod,
    SyncRegisteredMethod,
)
from jsonic_rpc._internal.abstractions.serializing import BaseLoader
from jsonic_rpc._internal.types import Params, Result

DependsMetadata = "DependsMetadata"

T = TypeVar("T")
Context = TypeVar("Context")


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
