from inspect import Parameter, Signature, signature
from types import NoneType
from typing import Annotated, Sequence, get_args, get_origin

from jsonic_rpc._internal.abstractions.di import Depends
from jsonic_rpc._internal.abstractions.method import Method, RegisteredMethod


def method_is_for_notification(method_signature: Signature) -> bool:
    return_annotation = method_signature.return_annotation
    if get_origin(return_annotation) is Annotated:
        return_annotation = get_args(return_annotation)[0]

    return return_annotation in (None, NoneType, Signature.empty)


def method_is_by_position(method_signature: Signature) -> bool:
    args = method_non_depends_args(method_signature)
    return len(args) == 1 and args[0].kind == Parameter.VAR_POSITIONAL


def _parameter_is_dependency(parameter: Parameter):
    annotation = parameter.annotation
    return get_origin(annotation) is Annotated or any(
        [isinstance(arg, Depends) for arg in get_args(annotation)]
    )


def method_non_depends_args(method_signature: Signature) -> Sequence[Parameter]:
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
            "Cannot access method __name__ attribute, so you have to explicitly specify method name"
        )
    return method_name


def make_registered(method: Method, name: str | None = None) -> RegisteredMethod:
    method_signature = signature(method)
    is_notification = method_is_for_notification(method_signature)
    is_by_position = method_is_by_position(method_signature)

    return RegisteredMethod(
        name=get_method_name(method, name),
        is_notification=is_notification,
        is_by_position=is_by_position,
        origin=method,
    )
