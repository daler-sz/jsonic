from inspect import Parameter, signature
from typing import Any, get_origin, Annotated, get_args

from dishka import Container
from dishka.integrations.base import wrap_injection

from jsonic_rpc._internal.abstractions.di import BaseDiInjector, Depends
from jsonic_rpc._internal.abstractions.method import RegisteredMethod
from jsonic_rpc._internal.abstractions.serializing import BaseLoader, MethodArgs
from jsonic_rpc._internal.method_introspection import method_non_depends_args
from jsonic_rpc._internal.types import Params


def default_parse_dependency(
    parameter: Parameter,
    hint: Any,
) -> Any:
    """Vendored from Dishka source"""
    if get_origin(hint) is not Annotated:
        return None
    dep = next(
        (arg for arg in get_args(hint) if isinstance(arg, Depends)),
        None,
    )
    if not dep:
        return None
    if dep.param is None:
        return get_args(hint)[0]
    else:
        return dep.param


class DiInjector(BaseDiInjector):
    def __init__(self, container: Container):
        self._container = container

    def call_injected(
        self,
        method: RegisteredMethod,
        loader: BaseLoader,
        params: Params,
    ) -> RegisteredMethod:
        non_dep_args = method_non_depends_args(signature(method.origin))
        loaded_args = loader.load_args(method, non_dep_args, params)

        with self._container({MethodArgs: loaded_args}) as subcontainer:
            injected = wrap_injection(
                method.origin, container_getter=lambda a, b: subcontainer, parse_dependency=default_parse_dependency
            )
            return injected(*loaded_args.positionals, **loaded_args.keywords)

    async def async_call_injected(
        self,
        method: RegisteredMethod,
        loader: BaseLoader,
        params: Params,
    ) -> RegisteredMethod:
        non_dep_args = method_non_depends_args(method)
        loaded_args = loader.load_args(method, non_dep_args, params)

        async with self._container({MethodArgs: loaded_args}) as subcontainer:
            injected = wrap_injection(
                method.origin, container_getter=lambda: subcontainer, parse_dependency=default_parse_dependency
            )
            return await injected(*loaded_args.positionals, **loaded_args.keywords)
