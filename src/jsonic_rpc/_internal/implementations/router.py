from contextlib import suppress
from dataclasses import dataclass, field
from typing import MutableMapping, MutableSequence

from jsonic_rpc._internal.abstractions.exceptions import MethodNotFound
from jsonic_rpc._internal.abstractions.method import Method, RegisteredMethod
from jsonic_rpc._internal.abstractions.router import BaseRouter
from jsonic_rpc._internal.method_introspection import make_registered


@dataclass
class Router(BaseRouter):
    prefix: str = ""
    routes: MutableMapping[str, RegisteredMethod] = field(
        default_factory=dict, init=False
    )
    routers: MutableSequence[BaseRouter] = field(
        default_factory=list, init=False
    )

    def _make_path(self, name):
        if self.prefix:
            return f"{self.prefix}.{name}"
        return name

    def _register_method(
        self,
        method: Method,
        name: str | None,
        allow_notifications: bool,
        allow_requests: bool,
    ) -> RegisteredMethod:
        registered_method: RegisteredMethod = make_registered(
            method, allow_notifications, allow_requests, name
        )
        path = self._make_path(registered_method.name)
        self.routes[path] = registered_method
        return registered_method

    def include_router(self, router: "BaseRouter") -> None:
        self.routers.append(router)
        if isinstance(router, Router):
            for path, method in router.routes.items():
                new_path = self._make_path(path)
                self.routes[new_path] = method

    def get_method(self, path: str) -> RegisteredMethod:
        try:
            return self.routes[path]
        except KeyError:
            for router in self.routers:
                with suppress(MethodNotFound):
                    return router.get_method(path)
            raise MethodNotFound(message="Method not found", data=path)
