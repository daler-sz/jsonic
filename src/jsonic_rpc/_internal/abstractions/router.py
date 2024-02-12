from abc import ABC, abstractmethod
from typing import Callable, final, overload

from jsonic_rpc._internal.abstractions.method import Method, RegisteredMethod


class BaseRouter(ABC):
    @abstractmethod
    def _register_method(
        self,
        method: Method,
        name: str | None,
        allow_notifications: bool,
        allow_requests: bool,
    ) -> RegisteredMethod:
        ...

    @abstractmethod
    def include_router(self, router: "BaseRouter") -> None:
        ...

    @abstractmethod
    def get_method(self, path: str) -> RegisteredMethod:
        ...

    @overload
    def method(
        self,
        method: Method,
        name: str | None = None,
    ) -> RegisteredMethod:
        ...

    @overload
    def method(
        self,
        method: None = None,
        name: str | None = None,
        allow_notifications: bool = True,
        allow_requests: bool = True,
    ) -> Callable[[Method], RegisteredMethod]:
        ...

    @final
    def method(
        self,
        method=None,
        name=None,
        allow_notifications=True,
        allow_requests=True,
    ):
        if not method:

            def decorator(method: Method):
                return self._register_method(
                    method, name, allow_notifications, allow_requests
                )

            return decorator

        return self._register_method(
            method, name, allow_notifications, allow_requests
        )
