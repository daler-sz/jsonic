from functools import partial
from inspect import Parameter, signature
from typing import Any, Mapping, get_args

from jsonic_rpc._internal.abstractions.di import DiInjector
from jsonic_rpc._internal.abstractions.method import RegisteredMethod
from jsonic_rpc._internal.abstractions.serializing import BaseLoader
from jsonic_rpc._internal.method_introspection import method_depends_args, method_non_depends_args
from jsonic_rpc._internal.types import Params


class SimpleDiInjector(DiInjector):
    """Silly di container. Not recommended for production"""

    def __init__(self, container: Mapping[Any, Any]):
        self.container = container

    def inject(
        self,
        method: RegisteredMethod,
        loader: BaseLoader,
        params: Params,
    ) -> RegisteredMethod:
        method_signature = signature(method.origin)

        non_dep_args = method_non_depends_args(method_signature)
        dep_args = method_depends_args(method_signature)

        positionals, nameds = loader.load_args(method, non_dep_args, params)
        deps = {}

        for dep_arg in dep_args:
            if dep_arg.kind == Parameter.POSITIONAL_ONLY:
                raise TypeError("Positional only DI dependencies are not supported")

            tp = get_args(dep_arg.annotation)[0]
            dep = self.container[tp]
            deps[dep_arg.name] = dep

        return type(method)(
            name=method.name,
            allow_notifications=method.allow_notifications,
            allow_requests=method.allow_requests,
            is_by_position=method.is_by_position,
            origin=partial(method, *positionals, **nameds, **deps),
        )
