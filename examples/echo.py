from dataclasses import dataclass

from jsonic_rpc import (
    Router,
    Processor,
    MapBasedExceptionConfiguration,
    SimpleDumper,
    SimpleLoader,
    SimpleDiInjector,
)

main_router = Router()


@dataclass
class InvalidText(Exception):
    msg: str
    data: str


@main_router.method
def echo(text: str) -> str:
    if text == "invalid":
        raise InvalidText(msg="given text is invalid", data=text)
    return text


processor = Processor(
    router=main_router,
    exception_configuration=MapBasedExceptionConfiguration(
        map_={
            InvalidText: -32001,
        },
        message_getter=lambda exc: exc.msg,
        data_getter=lambda exc: exc.data
    ),
    loader=SimpleLoader(),
    dumper=SimpleDumper(),
    di_injector=SimpleDiInjector({}),
)


assert processor.process_single({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "echo",
    "params": {
        "text": "hello"
    }
}) == {
    "id": 1,
    "jsonrpc": "2.0",
    "result": "hello"
}

assert processor.process_single({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "echo",
    "params": {
        "text": "invalid"
    }
}) == {
    "id": 1,
    "jsonrpc": "2.0",
    "error": {
        "code": -32001,
        "message": "given text is invalid",
        "data": "invalid"
    }
}
