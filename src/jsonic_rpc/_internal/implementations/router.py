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
    routers: MutableSequence[BaseRouter] = field(default_factory=list, init=False)

    def _get_prefix(self):
        return f"{self.prefix}." if self.prefix else ""

    def _register_method(self, method: Method, name: str | None) -> RegisteredMethod:
        registered_method = make_registered(method, name)
        self.routes[f"{self._get_prefix()}{registered_method.name}"] = registered_method
        return registered_method

    def include_router(self, router: "BaseRouter") -> None:
        self.routers.append(router)
        if isinstance(router, Router):
            for name, method in router.routes.items():
                self.routes[f"{self._get_prefix()}{name}"] = method

    def get_method(self, path: str) -> RegisteredMethod:
        try:
            return self.routes[path]
        except KeyError:
            for router in self.routers:
                with suppress(MethodNotFound):
                    return router.get_method(path)
            raise MethodNotFound(message="Method not found", data=path)
