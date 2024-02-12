from abc import ABC, abstractmethod
from dataclasses import dataclass
from inspect import Parameter
from typing import Any, Mapping, Sequence

from jsonic_rpc._internal.abstractions.exceptions import JsonRpcError
from jsonic_rpc._internal.abstractions.method import RegisteredMethod
from jsonic_rpc._internal.types import InputMapping, Message, OutputMapping, Params, Request, Response

ArgValue = Any


@dataclass
class MethodArgs:
    positionals: Sequence[ArgValue]
    keywords: Mapping[str, ArgValue]
    map_: Mapping[str, ArgValue]


class BaseLoader(ABC):
    @abstractmethod
    def load_message(self, data: InputMapping) -> Message:
        ...

    @abstractmethod
    def load_args(
        self,
        registered_method: RegisteredMethod,
        method_args: Sequence[Parameter],
        params: Params,
    ) -> MethodArgs:
        ...


class BaseDumper(ABC):
    @abstractmethod
    def dump_response(self, response: Response) -> OutputMapping:
        ...

    @abstractmethod
    def dump_exception(
        self,
        exception: JsonRpcError,
        request: Request | None = None,
    ) -> OutputMapping:
        ...
