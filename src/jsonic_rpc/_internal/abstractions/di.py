from abc import ABC, abstractmethod
from typing import Annotated, Any, TypeVar

from jsonic_rpc._internal.abstractions.method import SyncRegisteredMethod, AsyncRegisteredMethod
from jsonic_rpc._internal.abstractions.serializing import BaseLoader
from jsonic_rpc._internal.types import Params, SuccessResponse


class Depends:
    def __init__(self, param: Any = None):
        self.param = param


T = TypeVar("T")
Dependency = Annotated[T, Depends()]


class BaseDiInjector(ABC):
    @abstractmethod
    def call_injected(
        self,
        method: SyncRegisteredMethod,
        loader: BaseLoader,
        params: Params,
    ) -> SuccessResponse:
        ...

    @abstractmethod
    async def async_call_injected(
        self,
        method: AsyncRegisteredMethod,
        loader: BaseLoader,
        params: Params,
    ) -> SuccessResponse:
        ...
