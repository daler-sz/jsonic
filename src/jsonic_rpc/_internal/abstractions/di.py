from abc import ABC, abstractmethod
from typing import Annotated, Any, TypeVar

from jsonic_rpc._internal.abstractions.method import RegisteredMethod
from jsonic_rpc._internal.abstractions.serializing import BaseLoader
from jsonic_rpc._internal.types import Params


class Depends:
    def __init__(self, param: Any = None):
        self.param = param


T = TypeVar("T")
Dependency = Annotated[T, Depends()]


class DiInjector(ABC):
    @abstractmethod
    def inject(
        self, method: RegisteredMethod, loader: BaseLoader, params: Params
    ) -> RegisteredMethod:
        ...
