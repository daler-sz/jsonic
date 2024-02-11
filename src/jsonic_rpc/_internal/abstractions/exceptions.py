from dataclasses import dataclass
from typing import Any, Literal


@dataclass(kw_only=True)
class JsonRpcError(Exception):
    code: int
    message: str
    data: Any


@dataclass
class ParseError(JsonRpcError):
    code: Literal[-32700] = -32700
    message: str = "Cannot parse request object"


@dataclass
class InvalidRequest(JsonRpcError):
    code: Literal[-32600] = -32600
    message: str = "Invalid request object"


@dataclass
class MethodNotFound(JsonRpcError):
    code: Literal[-32601] = -32601
    message: str = "Method not found"


@dataclass
class InvalidParams(JsonRpcError):
    code: Literal[-32602] = -32602
    message: str = "Invalid params"


@dataclass
class InternalError(JsonRpcError):
    code: Literal[-32603] = -32603
    message: str = "Unexpected error"
