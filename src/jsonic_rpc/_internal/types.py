from dataclasses import dataclass
from typing import Any, Iterable, Literal, Mapping

RequestId = int | str | None
Params = Iterable | Mapping | None


@dataclass
class JsonRpc20:
    jsonrpc: Literal["2.0"]


@dataclass(kw_only=True)
class BaseMessage(JsonRpc20):
    method: str
    params: Params = None


@dataclass
class Notification(BaseMessage):
    pass


@dataclass
class Request(BaseMessage):
    id: RequestId


Message = Notification | Request


@dataclass
class BaseResponse(JsonRpc20):
    id: RequestId


@dataclass
class SuccessResponse(BaseResponse):
    result: Any


@dataclass
class ErrorResponse(BaseResponse):
    error: "Error"


@dataclass
class Error:
    code: int
    message: str
    data: Any


Response = SuccessResponse | ErrorResponse

InputMapping = Mapping
OutputMapping = Mapping
