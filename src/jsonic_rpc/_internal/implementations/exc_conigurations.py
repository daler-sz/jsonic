from dataclasses import dataclass
from typing import Any, Callable, Mapping, TypeVar, cast

from jsonic_rpc._internal.abstractions.exception_handling import (
    BaseExceptionConfiguration,
)
from jsonic_rpc._internal.abstractions.exceptions import JsonRpcError
from jsonic_rpc._internal.abstractions.serializing import BaseDumper
from jsonic_rpc._internal.types import OutputMapping, Request

T = TypeVar("T", bound=Exception)

MessageGetter = Callable[[Exception], str]
DataGetter = Callable[[Exception], Any]

MapValue = int | tuple[int, MessageGetter, DataGetter]


def default_message_getter(exc: Exception):
    return str(exc)


def default_data_getter(exc: Exception):
    return exc.args


@dataclass
class MapBasedExceptionConfiguration(BaseExceptionConfiguration[T]):
    map_: Mapping[type[Exception], MapValue]
    message_getter: MessageGetter = default_message_getter
    data_getter: DataGetter = default_data_getter

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
