import collections
from dataclasses import dataclass
from typing import Any

from jsonic_rpc._internal.abstractions.di import BaseDiInjector
from jsonic_rpc._internal.abstractions.exception_handling import BaseExceptionConfiguration
from jsonic_rpc._internal.abstractions.exceptions import InvalidParams, InvalidRequest
from jsonic_rpc._internal.abstractions.method import AsyncRegisteredMethod, RegisteredMethod
from jsonic_rpc._internal.abstractions.processor import BaseProcessor
from jsonic_rpc._internal.abstractions.router import BaseRouter
from jsonic_rpc._internal.abstractions.serializing import BaseDumper, BaseLoader
from jsonic_rpc._internal.types import Message, Notification, Request, SuccessResponse, Result

Mapping = collections.abc.Mapping


@dataclass
class Processor(BaseProcessor):
    router: BaseRouter
    exception_configuration: BaseExceptionConfiguration
    loader: BaseLoader
    dumper: BaseDumper
    di_injector: BaseDiInjector

    def _validate_message(self, message: Message, method: RegisteredMethod, async_: bool) -> None:
        path = message.method

        method_is_async = isinstance(method, AsyncRegisteredMethod)
        if method_is_async and not async_:
            raise TypeError(f"Method {path} is async, but it is called as sync method")

        if not method_is_async and async_:
            raise TypeError(f"Method {path} is sync, but it is called as async method")

        if not method.allow_requests and isinstance(message, Request):
            raise InvalidRequest(
                message=f"Method {path} can not process no-notification requests. "
                f"Please, consider do not specifying id member in request body",
                data=path,
            )

        if not method.allow_notifications and isinstance(message, Notification):
            raise InvalidRequest(
                message=f"Method {path} can not process notifications. "
                f"Please, consider specifying id member in request body",
                data=path,
            )

        if method.is_by_position and isinstance(message.params, Mapping):
            raise InvalidParams(
                message=f"Method {path} takes positional params. "
                f"Please, consider specifying params member as an array",
                data={"params": message.params, "method": path},
            )

        if not method.is_by_position and not isinstance(message.params, Mapping):
            raise InvalidParams(
                message=f"Method {path} takes params by names. "
                f"Please, consider specifying params member as an object",
                data={"params": message.params, "method": path},
            )

    def _process_message(self, message: Message) -> Any:
        method = self.router.get_method(message.method)
        self._validate_message(message, method, async_=False)
        return self.di_injector.call_injected(method, self.loader, message.params)

    def _process_notification(self, notification: Notification) -> None:
        self._process_message(notification)

    def _process_request(self, request: Request) -> SuccessResponse:
        result = self._process_message(request)
        return SuccessResponse(id=request.id, jsonrpc=request.jsonrpc, result=result)

    async def _async_process_message(self, message: Message) -> Result:
        method = self.router.get_method(message.method)
        self._validate_message(message, method, async_=True)
        return await self.di_injector.async_call_injected(method, self.loader, message.params)

    async def _async_process_notification(self, notification: Notification) -> None:
        await self._async_process_message(notification)

    async def _async_process_request(self, request: Request) -> SuccessResponse:
        result = await self._async_process_message(request)
        return SuccessResponse(id=request.id, jsonrpc=request.jsonrpc, result=result)
