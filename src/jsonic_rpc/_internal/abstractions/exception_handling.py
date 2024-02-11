from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from jsonic_rpc._internal.abstractions.serializing import BaseDumper
from jsonic_rpc._internal.types import OutputMapping, Request

T = TypeVar("T", bound=Exception)


@dataclass
class BaseExceptionConfiguration(ABC, Generic[T]):
    @abstractmethod
    def filter_map(self, exception: Exception) -> T | None:
        ...

    @abstractmethod
    def dump(
        self,
        dumper: BaseDumper,
        exception: T,
        request: Request | None = None,
    ) -> OutputMapping:
        ...
