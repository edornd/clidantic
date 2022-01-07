import logging

from click.testing import CliRunner
from pydantic import ValidationError

from examples.typing.container_types import cli as cli2
from examples.typing.primitive_types import cli as cli1

LOG = logging.getLogger(__name__)


def test_primitive_types(runner: CliRunner):
    result = runner.invoke(cli1, ["--help"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: status [OPTIONS]" in result.output
    assert "--name TEXT" in result.output
    assert "--count INT" in result.output
    assert "--amount FLOAT" in result.output
    assert "--paid / --no-paid" in result.output
    assert "--beep-bop BYTES" in result.output

    assert "Show this message and exit." in result.output
    assert result.exit_code == 0

    result = runner.invoke(cli1, [])
    assert result.exit_code == 1
    assert not result.output
    assert isinstance(result.exception, ValidationError)

    result = runner.invoke(cli1, ["--name=log", "--count=1", "--amount=34.52", "--paid", "--beep-bop=raw"])
    LOG.debug(result.output)
    assert "Register: log" in result.output
    assert "bills:    1" in result.output
    assert "amount:   $34.52" in result.output
    assert "status:   closed" in result.output
    assert "bytes:    b'raw'" in result.output
    assert not result.exception
    assert result.exit_code == 0


def test_containers(runner: CliRunner):
    result = runner.invoke(cli2, ["--help"])
    LOG.debug(result.output)
    assert not result.exception
    output = " ".join(result.output.split())
    assert "Usage: run [OPTIONS]" in output
    assert "Options:" in output
    assert "--simple-list TEXT [default: (empty list)]" in output
    assert "--list-of-ints INTEGER [default: (empty list)]" in output
    assert "--simple-tuple TEXT [default: (empty tuple)]" in output
    assert "--multi-typed-tuple <INTEGER FLOAT TEXT BOOLEAN>... [default: (empty tuple)]" in output
    assert "--simple-dict JSON [default: (empty dict)]" in output
    assert "--dict-str-float JSON [default: (empty dict)]" in output
    assert "--simple-set TEXT [default: (empty set)]" in output
    assert "--set-bytes BYTES [default: (empty set)]" in output
    assert "--frozen-set INTEGER [default: (empty frozenset)]" in output
    assert "--none-or-str TEXT" in output
    assert "--sequence-of-ints INTEGER [default: (empty Sequence)]" in output
    assert "--compound JSON [default: (empty dict)]" in output
    assert "--deque INTEGER [default: (empty deque)]" in output
    assert "--help Show this message and exit." in output
    assert result.exit_code == 0
    # run empty (all default to None)
    expected = """
    simple_list         : None
    list_of_ints        : None
    simple_tuple        : None
    multi_typed_tuple   : None
    simple_dict         : None
    dict_str_float      : None
    simple_set          : None
    set_bytes           : None
    frozen_set          : None
    none_or_str         : None
    sequence_of_ints    : None
    compound            : None
    deque               : None
    """
    expected = " ".join(expected.split())
    result = runner.invoke(cli2, [])
    LOG.debug(result.output)
    assert not result.exception
    assert result.exit_code == 0
    output = " ".join(result.output.split())
    assert expected in output
    # run with custom params
    args = [
        "--simple-list=a",
        "--simple-list=b",
        "--simple-list=c",
        "--list-of-ints=1",
        "--list-of-ints=2",
        "--list-of-ints=3",
        "--simple-tuple=x",
        "--simple-tuple=12",
        "--multi-typed-tuple=12",
        "2.0",
        "hi",
        "true",
        '--simple-dict={"hello": "hola"}',
        '--dict-str-float={"mean": 23.45}',
        "--simple-set=abc",
        "--simple-set=123",
        "--set-bytes=a",
        "--set-bytes=b",
        "--frozen-set=1",
        "--frozen-set=2",
        "--none-or-str=string",
        "--sequence-of-ints=1",
        "--sequence-of-ints=2",
        '--compound={"geometry": [[1],[2],[3]]}',
        "--deque=1",
        "--deque=2",
    ]
    result = runner.invoke(cli2, args)
    LOG.debug(result.output)
    assert not result.exception
    assert result.exit_code == 0
    expected_a = """
    simple_list         : ['a', 'b', 'c']
    list_of_ints        : [1, 2, 3]
    simple_tuple        : ('x', '12')
    multi_typed_tuple   : (12, 2.0, 'hi', True)
    simple_dict         : {'hello': 'hola'}
    dict_str_float      : {'mean': 23.45}
    """
    expected_b = """
    frozen_set          : frozenset({1, 2})
    none_or_str         : string
    sequence_of_ints    : (1, 2)
    compound            : {'geometry': [{1}, {2}, {3}]}
    deque               : deque([1, 2])
    """
    # sets do not have deterministic order, there might be a better way, but whatever
    # let me know if you find it
    expected_set_1 = ["{'abc', '123'}", "{'123', 'abc'}"]
    expected_set_2 = ["{b'a', b'b'}", "{b'b', b'a'}"]
    expected_a = " ".join(expected_a.strip().rstrip().split())
    expected_b = " ".join(expected_b.strip().rstrip().split())
    output = " ".join(result.output.strip().rstrip().split())
    assert expected_a in output
    assert expected_b in output
    assert any(exp in output for exp in expected_set_1)
    assert any(exp in output for exp in expected_set_2)
