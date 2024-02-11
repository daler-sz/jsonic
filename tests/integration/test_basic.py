from unittest.mock import ANY

from jsonic_rpc import MapBasedExceptionConfiguration, Processor, Router, SimpleDiInjector, SimpleDumper, SimpleLoader

router = Router(prefix="main")


@router.method
def echo(text: str) -> str:
    return text


processor = Processor(
    router=router,
    exception_configuration=MapBasedExceptionConfiguration(
        {},
    ),
    loader=SimpleLoader(),
    dumper=SimpleDumper(),
    di_injector=SimpleDiInjector({}),
)


def test_success():
    assert processor.process_single(
        {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "main.echo",
            "params": {"text": "Hello world!"},
        }
    ) == {"id": 1, "jsonrpc": "2.0", "result": "Hello world!"}


def test_error():
    assert processor.process_single({"id": 1, "params": {"text": "hello"}}) == {
        "id": None,
        "jsonrpc": "2.0",
        "error": {"code": -32600, "message": ANY, "data": ANY},
    }

    assert processor.process_single(
        {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "main.not_existing_method",
            "params": {"text": "hello"},
        }
    ) == {
        "id": 1,
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": ANY, "data": ANY},
    }

    assert processor.process_single(
        {"id": 1, "jsonrpc": "2.0", "method": "main.echo", "params": {"tex": "hello"}}
    ) == {
        "id": 1,
        "jsonrpc": "2.0",
        "error": {"code": -32602, "message": ANY, "data": ANY},
    }
