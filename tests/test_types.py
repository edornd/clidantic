import json
import logging
from typing import Dict, List, Literal, Mapping, Type

import pytest
from click import Command, Context
from click.exceptions import BadParameter
from click.testing import CliRunner
from pydantic import BaseModel, Json

from clidantic import Parser
from clidantic.types import BytesType, JsonType, LiteralChoice, ModuleType

LOG = logging.getLogger(__name__)


def test_bytes_type(runner: CliRunner):
    cli = Parser()

    class Model(BaseModel):
        test: bytes

    @cli.command()
    def run(config: Model):
        return config.test

    assert len(cli.commands) == 1
    # there's only one command, with one param
    cmd: Command = cli.commands[0]
    byte_type: BytesType = cmd.params[0].type
    assert isinstance(byte_type, BytesType)
    # test help with custom name
    result = runner.invoke(cli, ["--help"])
    assert not result.exception
    assert result.exit_code == 0
    assert "--test BYTES" in result.output
    # test raw conversion first
    with pytest.raises(BadParameter):
        byte_type.convert(123, cmd.params[0], Context(cmd))
    result = byte_type.convert(b"raw", cmd.params[0], Context(cmd))
    assert isinstance(result, bytes)
    result = byte_type.convert("string", cmd.params[0], Context(cmd))
    assert isinstance(result, bytes)
    # test conversion during CLI invocation
    result = runner.invoke(cli, ["--test=string"], standalone_mode=False)
    assert result.exit_code == 0
    assert not result.exception
    assert result.return_value == b"string"


class DictSimple(BaseModel):
    test: dict


class DictTyped(BaseModel):
    test: Dict[str, str]


class DictTypedMulti(BaseModel):
    test: Dict[str, float]


class DictCompound(BaseModel):
    test: Dict[str, List[bool]]


class DictJSON(BaseModel):
    test: Json


@pytest.mark.parametrize(
    ("config_class", "expected", "expected_type"),
    [
        (DictSimple, {"hello": "hola"}, Mapping),
        (DictTyped, {"hello": "hola"}, Mapping),
        (DictTypedMulti, {"hello": 2.0}, Mapping),
        (DictCompound, {"a": [True, False]}, Mapping),
        (DictJSON, {"a": ["hello", "world"]}, str),
    ],
)
def test_json_type(runner: CliRunner, config_class: Type[BaseModel], expected: dict, expected_type: Type):
    cli = Parser()

    @cli.command()
    def run(config: config_class):
        return config.test

    assert len(cli.commands) == 1
    # there's only one command, with one param
    cmd: Command = cli.commands[0]
    dict_type: JsonType = cmd.params[0].type
    assert isinstance(dict_type, JsonType)
    # test help with custom name
    result = runner.invoke(cli, ["--help"])
    assert not result.exception
    assert result.exit_code == 0
    assert "--test JSON" in result.output
    # test raw conversion first
    raw = json.dumps(expected)
    result = dict_type.convert(raw, cmd.params[0], Context(cmd))
    assert isinstance(result, expected_type)
    # special case for Json fields that require a raw string
    # otherwise we just test that an error is raised for non-valid json
    if expected_type == str:
        result = json.loads(result)
    else:
        with pytest.raises(BadParameter):
            dict_type.convert("{wrong: string}", cmd.params[0], Context(cmd))

    assert result == expected
    result = dict_type.convert(expected, cmd.params[0], Context(cmd))
    assert isinstance(result, type(expected))
    assert result == expected
    # test conversion during CLI invocation
    result = runner.invoke(cli, [f"--test={raw}"], standalone_mode=False)
    assert result.exit_code == 0
    assert not result.exception
    assert result.return_value == expected


def test_module_type(runner: CliRunner):
    from tests.module import TestClass

    class Settings(BaseModel):
        field: Type[TestClass] = None

    cli = Parser()

    @cli.command()
    def run(config: Settings):
        print(config.field)
        return config.field

    assert len(cli.commands) == 1
    # there's only one command, with one param
    cmd: Command = cli.commands[0]
    dict_type: ModuleType = cmd.params[0].type
    assert isinstance(dict_type, ModuleType)
    result = runner.invoke(cli, ["--help"])
    assert not result.exception
    assert result.exit_code == 0
    assert "--field MODULE" in result.output
    # test raw conversion first
    result = dict_type.convert("tests.module.TestClass", cmd.params[0], Context(cmd))
    assert result is TestClass
    # test conversion during CLI invocation
    result = runner.invoke(cli, [f"--field=tests.module.TestClass"], standalone_mode=False)
    LOG.debug(result.output)
    assert not result.exception


class StringLiteral(BaseModel):
    test: Literal["one", "two"]


class IntLiteral(BaseModel):
    test: Literal[1, 2]


class BoolLiteral(BaseModel):
    test: Literal[True, False]


class MixedLiteral(BaseModel):
    test: Literal["one", 2]


@pytest.mark.parametrize(
    ("config_class", "expected"),
    [
        (StringLiteral, ["one", "two"]),
        (IntLiteral, [1, 2]),
        (BoolLiteral, [True, False]),
        (MixedLiteral, None),
    ],
)
def test_literal_type(runner: CliRunner, config_class: Type[BaseModel], expected: list):
    cli = Parser()

    if expected is not None:

        @cli.command()
        def run(config: config_class):
            return config.test

    else:
        with pytest.raises(AssertionError):

            @cli.command()
            def run(config: config_class):
                return config.test

        return

    assert len(cli.commands) == 1
    # there's only one command, with one param
    cmd: Command = cli.commands[0]
    lit_type: LiteralChoice = cmd.params[0].type
    assert isinstance(lit_type, LiteralChoice)
    # test help with custom name
    result = runner.invoke(cli, ["--help"])
    assert not result.exception
    assert result.exit_code == 0
    assert "--test [" in result.output
    # test raw conversion first
    if expected is not None:
        for value in expected:
            expected_type = type(value)
            result = lit_type.convert(str(value), cmd.params[0], Context(cmd))
            assert isinstance(result, expected_type)
