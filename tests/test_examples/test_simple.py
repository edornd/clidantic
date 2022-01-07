import logging

import pytest
from click.testing import CliRunner
from pydantic import ValidationError

from clidantic import Parser
from examples.simple.simple_cmd import cli as cli1
from examples.simple.simple_default import cli as cli3
from examples.simple.simple_help import cli as cli2

LOG = logging.getLogger(__name__)


def test_no_commands(runner: CliRunner):
    cli = Parser()

    with pytest.raises(ValueError):
        runner.invoke(cli, [])
    with pytest.raises(ValueError):
        runner.invoke(cli, ["--help"])


def test_empty_command(runner: CliRunner):
    cli = Parser()

    @cli.command()
    def empty():
        """Hello World!"""
        print("Done!")

    result = runner.invoke(cli, ["--help"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Hello World!" in result.output
    assert "Show this message and exit." in result.output
    assert result.exit_code == 0
    assert "Done!" not in result.output

    result = runner.invoke(cli, [])
    assert not result.exception
    assert "Done!" in result.output
    assert result.exit_code == 0


def test_simple_command(runner: CliRunner):
    result = runner.invoke(cli1, ["--help"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: hello [OPTIONS]" in result.output
    assert "--name TEXT" in result.output
    assert "Show this message and exit." in result.output
    assert result.exit_code == 0

    result = runner.invoke(cli1, ["--name=Grievous"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Hello there, Grievous!" in result.output
    assert result.exit_code == 0

    result = runner.invoke(cli1, [])
    LOG.debug(result.output)
    assert isinstance(result.exception, ValidationError)
    assert not result.output
    assert result.exit_code == 1


def test_simple_command_help(runner: CliRunner):
    result = runner.invoke(cli2, ["--help"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: hello [OPTIONS]" in result.output
    assert "--name TEXT" in result.output
    assert "How I should call you, for instance 'General Kenobi'" in result.output
    assert "Show this message and exit." in result.output
    assert result.exit_code == 0

    result = runner.invoke(cli2, ["--name=Grievous"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Hello there, Grievous!" in result.output
    assert result.exit_code == 0

    result = runner.invoke(cli2, [])
    LOG.debug(result.output)
    assert isinstance(result.exception, ValidationError)
    assert not result.output
    assert result.exit_code == 1


def test_simple_command_default(runner: CliRunner):
    result = runner.invoke(cli3, ["--help"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: hello [OPTIONS]" in result.output
    assert "--name TEXT" in result.output
    assert "How I should call you, for instance 'General Kenobi'" in result.output
    assert "Show this message and exit." in result.output
    assert result.exit_code == 0

    result = runner.invoke(cli3, ["--name=Grievous"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Hello there, Grievous!" in result.output
    assert result.exit_code == 0

    result = runner.invoke(cli3, [])
    LOG.debug(result.output)
    assert not result.exception
    assert "Hello there, Mark!" in result.output
    assert result.exit_code == 0
