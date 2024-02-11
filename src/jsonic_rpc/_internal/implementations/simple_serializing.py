import collections.abc
from inspect import Parameter
from typing import Any, Iterable, Sequence, cast

from jsonic_rpc._internal.abstractions.exceptions import InvalidParams, InvalidRequest, JsonRpcError
from jsonic_rpc._internal.abstractions.method import RegisteredMethod
from jsonic_rpc._internal.abstractions.serializing import BaseDumper, BaseLoader
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
        self, method: RegisteredMethod, method_args: Sequence[Parameter], params: Params
    ) -> tuple[Iterable[Any], Mapping[str, Any]]:
        if params is None:
            return [], {}

        if method.is_by_position:
            return params, {}

        #  for here params is already validated and we sure that it is Mapping
        params = cast(Mapping, params)
        params = dict(params)

        positionals = []
        nameds = {}

        for arg in method_args:
            try:
                if arg.kind == Parameter.POSITIONAL_ONLY:
                    positionals.append(params.pop(arg.name))
                elif arg.kind in (Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
                    nameds[arg.name] = params.pop(arg.name)
                elif arg.kind == Parameter.VAR_POSITIONAL:
                    positionals.extend(params.values())
                elif arg.kind == Parameter.VAR_KEYWORD:
                    nameds = {**nameds, **params}

            except KeyError:
                raise InvalidParams(message="Invalid params member in request body", data=arg.name)

        return positionals, nameds


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
