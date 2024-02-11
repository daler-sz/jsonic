from dataclasses import dataclass
from typing import Any, Protocol


class RequestMethodByName(Protocol):
    def __call__(self, *args, **kwargs) -> Any:
        ...


class RequestMethodByPosition(Protocol):
    def __call__(self, *args) -> Any:
        ...


class NotificationMethodByName(Protocol):
    def __call__(self, *args, **kwargs) -> None:
        ...


class NotificationMethodByPosition(Protocol):
    def __call__(self, *args) -> None:
        ...


RequestMethod = RequestMethodByPosition | RequestMethodByName
NotificationMethod = NotificationMethodByPosition | NotificationMethodByName

Method = RequestMethod | NotificationMethod


@dataclass(frozen=True)
class RegisteredMethod:
    name: str
    is_notification: bool
    is_by_position: bool
    origin: Method

    def __call__(self, *args, **kwargs):
        return self.origin(*args, **kwargs)
