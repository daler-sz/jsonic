import logging
from abc import ABC, abstractmethod
from typing import final

from jsonic_rpc._internal.abstractions.exception_handling import BaseExceptionConfiguration
from jsonic_rpc._internal.abstractions.exceptions import InternalError, InvalidRequest, JsonRpcError
from jsonic_rpc._internal.abstractions.serializing import BaseDumper, BaseLoader
from jsonic_rpc._internal.types import InputMapping, Notification, OutputMapping, Request, Response

logger = logging.getLogger("jsonic_rpc")


class BaseProcessor(ABC):
    loader: BaseLoader
    dumper: BaseDumper
    exception_configuration: BaseExceptionConfiguration

    @abstractmethod
    def _process_request(self, request: Request) -> Response:
        ...

    @abstractmethod
    def _process_notification(self, message: Notification) -> None:
        ...

    @final
    def process_single(self, data: InputMapping) -> OutputMapping | None:
        try:
            message = self.loader.load_message(data)
        except InvalidRequest as exc:
            return self.dumper.dump_exception(exc)

        if isinstance(message, Notification):
            return self._process_notification(message)

        try:
            response = self._process_request(message)
            return self.dumper.dump_response(response)

        except JsonRpcError as exc:
            return self.dumper.dump_exception(exc, message)

        except Exception as exc:
            filter_result = self.exception_configuration.filter_map(exc)
            if filter_result is not None:
                return self.exception_configuration.dump(self.dumper, filter_result, message)
            logger.exception("Unexpected exception", exc_info=exc, extra={"data": data})
            return self.dumper.dump_exception(InternalError(message="Unexpected error", data=data), message)
