import collections.abc
from inspect import Parameter
from typing import Sequence, cast

from jsonic_rpc._internal.abstractions.exceptions import InvalidParams, InvalidRequest, JsonRpcError
from jsonic_rpc._internal.abstractions.method import RegisteredMethod
from jsonic_rpc._internal.abstractions.serializing import BaseDumper, BaseLoader, MethodArgs
from jsonic_rpc._internal.types import (
    ErrorResponse,
    InputMapping,
    Message,
    Notification,
    OutputMapping,
    Params,
    Request,
    Response,
    SuccessResponse,
)

Mapping = collections.abc.Mapping


class SimpleLoader(BaseLoader):
    """Simple loader. Not recommended for production"""

    def load_message(self, data: InputMapping) -> Message:
        try:
            if data.get("id"):
                return Request(
                    jsonrpc=data["jsonrpc"],
                    method=data["method"],
                    params=data.get("params"),
                    id=data.get("id"),
                )
            else:
                return Notification(
                    jsonrpc=data["jsonrpc"],
                    method=data["method"],
                    params=data.get("params"),
                )
        except KeyError:
            raise InvalidRequest(message="Invalid request object", data=data)

    def load_args(
        self,
        method: RegisteredMethod,
        method_args: Sequence[Parameter],
        params: Params,
    ) -> MethodArgs:
        if params is None:
            return MethodArgs([], {}, {})

        if method.is_by_position:
            return MethodArgs(tuple(params), {}, {method_args[0].name: params})

        #  for here params is already validated and we sure that it is Mapping
        params = cast(Mapping, params)
        params = dict(params)

        positionals = []
        keywords = {}
        map_ = {}

        for arg in method_args:
            try:
                name = arg.name
                value = params.pop(name)
            except KeyError:
                raise InvalidParams(message="Invalid params member in request body", data=arg.name)

            if arg.kind == Parameter.POSITIONAL_ONLY:
                positionals.append(value)
                map_[name] = value
            elif arg.kind in (Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
                keywords[name] = value
                map_[name] = value
            elif arg.kind == Parameter.VAR_POSITIONAL:
                values = params.values()
                positionals.extend(values)
                map_[name] = values
            elif arg.kind == Parameter.VAR_KEYWORD:
                keywords = {**keywords, **params}
                map_[name] = params

        return MethodArgs(positionals, keywords, map_)


class SimpleDumper(BaseDumper):
    """Simple dumper. Not recommended for production"""

    def dump_response(self, response: Response) -> OutputMapping:
        if isinstance(response, ErrorResponse):
            return {
                "jsonrpc": response.jsonrpc,
                "id": response.id,
                "error": {
                    "code": response.error.code,
                    "message": response.error.message,
                    "data": response.error.data,
                },
            }
        elif isinstance(response, SuccessResponse):
            return {
                "jsonrpc": response.jsonrpc,
                "id": response.id,
                "result": response.result,
            }

    def dump_exception(
        self,
        exception: JsonRpcError,
        request: Request | None = None,
    ) -> OutputMapping:
        return {
            "jsonrpc": "2.0",
            "id": None if not request else request.id,
            "error": {
                "code": exception.code,
                "message": exception.message,
                "data": exception.data,
            },
        }
