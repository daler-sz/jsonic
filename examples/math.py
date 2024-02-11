from dataclasses import dataclass

from jsonic_rpc import (
    Router,
    Processor,
    MapBasedExceptionConfiguration,
    SimpleDumper,
    SimpleLoader,
    SimpleDiInjector,
    Dependency,
)

main_router = Router(prefix="main")
math_router = Router(prefix="math")


@dataclass
class InvalidCountArgs(Exception):
    msg: str
    allowed_count: int
    input_count: int


@math_router.method(name="sum")
def add(a: int, b: int) -> int:
    return a + b


@math_router.method
def subtract(*args) -> int:
    if len(args) != 2:
        raise InvalidCountArgs(
            msg="Can subtract exact 2 values",
            allowed_count=2,
            input_count=len(args)
        )
    return args[0] - args[1]


@math_router.method(name="multiplyByConstant")
def multiply_by_constant(number: int, multiplier: Dependency[int]) -> int:
    return number * multiplier


main_router.include_router(math_router)

processor = Processor(
    router=main_router,
    exception_configuration=MapBasedExceptionConfiguration(
        map_={
            InvalidCountArgs: (
                -32001,
                lambda exc: exc.msg,
                lambda exc: {"allowedCount": exc.allowed_count, "inputCount": exc.input_count}
            )
        },
        message_getter=lambda exc: exc.msg,
        data_getter=lambda exc: exc.data
    ),
    loader=SimpleLoader(),
    dumper=SimpleDumper(),
    di_injector=SimpleDiInjector({int: 3}),
)


assert processor.process_single({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "main.math.sum",
    "params": {
        "a": 3,
        "b": 2
    }
}) == {
    "id": 1,
    "jsonrpc": "2.0",
    "result": 5
}

assert processor.process_single({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "main.math.subtract",
    "params": [3, 2]
}) == {
    "id": 1,
    "jsonrpc": "2.0",
    "result": 1
}

assert processor.process_single({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "main.math.subtract",
    "params": [3, 2, 1]
}) == {
    "id": 1,
    "jsonrpc": "2.0",
    "error": {
        "code": -32001,
        "message": "Can subtract exact 2 values",
        "data": {"allowedCount": 2, "inputCount": 3}
    }
}

assert processor.process_single({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "main.math.multiplyByConstant",
    "params": {
        "number": 3
    }
}) == {
    "id": 1,
    "jsonrpc": "2.0",
    "result": 9
}
