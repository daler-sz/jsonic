import collections
from dataclasses import dataclass

from jsonic_rpc._internal.abstractions.di import DiInjector
from jsonic_rpc._internal.abstractions.exception_handling import BaseExceptionConfiguration
from jsonic_rpc._internal.abstractions.exceptions import InvalidParams, MethodNotFound
from jsonic_rpc._internal.abstractions.method import RegisteredMethod
from jsonic_rpc._internal.abstractions.processor import BaseProcessor
from jsonic_rpc._internal.abstractions.router import BaseRouter
from jsonic_rpc._internal.abstractions.serializing import BaseDumper, BaseLoader
from jsonic_rpc._internal.types import Message, Notification, Request, SuccessResponse

Mapping = collections.abc.Mapping


@dataclass
class Processor(BaseProcessor):
    router: BaseRouter
    exception_configuration: BaseExceptionConfiguration
    loader: BaseLoader
    dumper: BaseDumper
    di_injector: DiInjector

    def _validate_message(
        self,
        message: Message,
        method: RegisteredMethod,
    ) -> None:
        path = message.method
        if not method.allow_requests and isinstance(message, Request):
            raise MethodNotFound(
                message=f"Method {path} can not process no-notification requests. "
                f"Please, consider do not specifying id member in request body",
                data=path,
            )

        if not method.allow_notifications and isinstance(message, Notification):
            raise MethodNotFound(
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

    def _process_message(self, message: Message) -> SuccessResponse | None:
        method = self.router.get_method(message.method)
        self._validate_message(message, method)
        injected_method = self.di_injector.inject(method, self.loader, message.params)
        return injected_method()

    def _process_notification(self, notification: Notification) -> None:
        self._process_message(notification)

    def _process_request(self, request: Request) -> SuccessResponse:
        result = self._process_message(request)
        return SuccessResponse(id=request.id, jsonrpc=request.jsonrpc, result=result)
