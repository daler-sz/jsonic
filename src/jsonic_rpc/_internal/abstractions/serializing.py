from abc import ABC, abstractmethod
from inspect import Parameter
from typing import Any, Iterable, Mapping, Sequence

from jsonic_rpc._internal.abstractions.exceptions import JsonRpcError
from jsonic_rpc._internal.abstractions.method import RegisteredMethod
from jsonic_rpc._internal.types import InputMapping, Message, OutputMapping, Params, Request, Response


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
    ) -> tuple[Iterable[Any], Mapping[str, Any]]:
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
