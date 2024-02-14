from dataclasses import dataclass
from inspect import Parameter, signature
from typing import Annotated, Any, get_args, get_origin

from dishka import AsyncContainer, Container
from dishka.integrations.base import wrap_injection

from jsonic_rpc._internal.abstractions.di import BaseDiInjector, Depends
from jsonic_rpc._internal.abstractions.method import RegisteredMethod
from jsonic_rpc._internal.abstractions.serializing import (
    BaseLoader,
    MethodArgs,
)
from jsonic_rpc._internal.method_introspection import method_non_depends_args
from jsonic_rpc._internal.types import Params, Result


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


@dataclass
class ContainersWrapper:
    sync_container: Container | None = None
    async_container: AsyncContainer | None = None

    def __post_init__(self):
        if not (self.sync_container or self.async_container):
            raise TypeError(
                "Neither sync_container nor async_container specifyied in "
                "Context constructor"
            )


class DiInjector(BaseDiInjector[ContainersWrapper]):
    def __init__(self, context: ContainersWrapper):
        self._sync_container = context.sync_container
        self._async_container = context.async_container

    def call_injected(
        self,
        method: RegisteredMethod,
        loader: BaseLoader,
        params: Params,
        context: ContainersWrapper | None,
    ) -> Result:
        non_dep_args = method_non_depends_args(signature(method.origin))
        loaded_args = loader.load_args(method, non_dep_args, params)
        container = context.sync_container if context else self._sync_container

        if not container:
            raise TypeError("Sync container is not specified")

        with container({MethodArgs: loaded_args}) as subcontainer:
            injected = wrap_injection(
                method.origin,
                container_getter=lambda a, b: subcontainer,
                parse_dependency=default_parse_dependency,
            )
            return injected(*loaded_args.positionals, **loaded_args.keywords)

    async def async_call_injected(
        self,
        method: RegisteredMethod,
        loader: BaseLoader,
        params: Params,
        context: ContainersWrapper | None,
    ) -> RegisteredMethod:
        non_dep_args = method_non_depends_args(signature(method.origin))
        loaded_args = loader.load_args(method, non_dep_args, params)
        container = (
            context.async_container if context else self._async_container
        )

        if not container:
            raise TypeError("Async container is not specified")

        async with container({MethodArgs: loaded_args}) as subcontainer:
            injected = wrap_injection(
                method.origin,
                container_getter=lambda a, b: subcontainer,  # type: ignore
                parse_dependency=default_parse_dependency,
                is_async=True,
            )
            return await injected(
                *loaded_args.positionals, **loaded_args.keywords
            )
