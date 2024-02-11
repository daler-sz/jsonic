from dataclasses import dataclass
from typing import Any, Protocol


class MethodByName(Protocol):
    def __call__(self, *args, **kwargs) -> Any:
        ...


class MethodByPosition(Protocol):
    def __call__(self, *args) -> Any:
        ...


Method = MethodByName | MethodByPosition


@dataclass(frozen=True)
class RegisteredMethod:
    name: str
    is_by_position: bool
    origin: Method
    allow_notifications: bool = True
    allow_requests: bool = True

    def __call__(self, *args, **kwargs):
        return self.origin(*args, **kwargs)
