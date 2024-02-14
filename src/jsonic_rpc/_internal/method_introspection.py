from inspect import Parameter, Signature, iscoroutinefunction, signature
from typing import Annotated, Sequence, get_args, get_origin

from jsonic_rpc._internal.abstractions.di import DependsMetadata
from jsonic_rpc._internal.abstractions.method import (
    AsyncRegisteredMethod,
    Method,
    RegisteredMethod,
    SyncRegisteredMethod,
)


def method_is_by_position(method_signature: Signature) -> bool:
    args = method_non_depends_args(method_signature)
    return len(args) == 1 and args[0].kind == Parameter.VAR_POSITIONAL


def _parameter_is_dependency(parameter: Parameter):
    annotation = parameter.annotation
    return get_origin(annotation) is Annotated and any(
        [arg == DependsMetadata for arg in get_args(annotation)]
    )


def method_non_depends_args(
    method_signature: Signature,
) -> Sequence[Parameter]:
    return [
        parameter
        for parameter in method_signature.parameters.values()
        if not _parameter_is_dependency(parameter)
    ]


def method_depends_args(method_signature: Signature) -> Sequence[Parameter]:
    return [
        parameter
        for parameter in method_signature.parameters.values()
        if _parameter_is_dependency(parameter)
    ]


def get_method_name(method: Method, name: str | None) -> str:
    if name:
        return name
    method_name = getattr(method, "__name__", None)
    if not method_name:
        raise ValueError(
            "Cannot access method __name__ attribute,"
            " so you have to explicitly specify method name"
        )
    return method_name


def make_registered(
    method: Method,
    allow_notifications: bool,
    allow_requests: bool,
    name: str | None = None,
) -> RegisteredMethod:
    method_signature = signature(method)
    is_by_position = method_is_by_position(method_signature)
    is_async = iscoroutinefunction(method)

    if is_async:
        return AsyncRegisteredMethod(
            name=get_method_name(method, name),
            allow_notifications=allow_notifications,
            allow_requests=allow_requests,
            is_by_position=is_by_position,
            origin=method,
        )

    return SyncRegisteredMethod(
        name=get_method_name(method, name),
        allow_notifications=allow_notifications,
        allow_requests=allow_requests,
        is_by_position=is_by_position,
        origin=method,
    )
