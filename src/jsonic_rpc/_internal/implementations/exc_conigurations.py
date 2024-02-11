from dataclasses import dataclass
from typing import Any, Callable, Mapping, TypeVar, cast

from jsonic_rpc._internal.abstractions.exception_handling import BaseExceptionConfiguration
from jsonic_rpc._internal.abstractions.exceptions import JsonRpcError
from jsonic_rpc._internal.abstractions.serializing import BaseDumper
from jsonic_rpc._internal.types import OutputMapping, Request

T = TypeVar("T", bound=Exception)

MESSAGE_GETTER = Callable[[Exception], str]
DATA_GETTER = Callable[[Exception], Any]

MAP_VALUE = int | tuple[int, MESSAGE_GETTER, DATA_GETTER]


def default_message_getter(exc: Exception):
    return str(exc)


def default_data_getter(exc: Exception):
    return exc.args


@dataclass
class MapBasedExceptionConfiguration(BaseExceptionConfiguration[T]):
    map_: Mapping[type[Exception], MAP_VALUE]
    message_getter: MESSAGE_GETTER = default_message_getter
    data_getter: DATA_GETTER = default_data_getter

    def filter_map(self, exception: Exception) -> T | None:
        if type(exception) in self.map_:
            return cast(T, exception)
        return None

    def dump(
        self,
        dumper: BaseDumper,
        exception: T,
        request: Request | None = None,
    ) -> OutputMapping:
        map_value = self.map_[type(exception)]

        if isinstance(map_value, int):
            return dumper.dump_exception(
                JsonRpcError(
                    code=map_value,
                    message=self.message_getter(exception),
                    data=self.data_getter(exception),
                ),
                request=request,
            )

        code, message_getter, data_getter = map_value
        return dumper.dump_exception(
            JsonRpcError(
                code=code,
                message=message_getter(exception),
                data=data_getter(exception),
            ),
            request=request,
        )
