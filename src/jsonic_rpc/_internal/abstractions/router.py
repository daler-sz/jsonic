from abc import ABC, abstractmethod
from typing import Callable, final, overload

from jsonic_rpc._internal.abstractions.method import Method, RegisteredMethod


class BaseRouter(ABC):
    @abstractmethod
    def _register_method(
        self, method: Method, name: str | None
    ) -> RegisteredMethod:
        ...

    @abstractmethod
    def include_router(self, router: "BaseRouter") -> None:
        ...

    @abstractmethod
    def get_method(self, path: str) -> RegisteredMethod:
        ...

    @overload
    def method(self, method: Method, name: str | None = None) -> RegisteredMethod:
        ...

    @overload
    def method(
        self, method: None = None, name: str | None = None
    ) -> Callable[[Method], RegisteredMethod]:
        ...

    @final
    def method(self, method=None, name=None):
        if not method:

            def decorator(method: Method):
                return self._register_method(method, name)

            return decorator

        return self._register_method(method, name)
