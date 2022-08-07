import logging
import subprocess

import pytest
from click.testing import CliRunner

from clidantic import Parser
from examples.simple import simple_cmd as mod1
from examples.simple import simple_default as mod3
from examples.simple import simple_help as mod2

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
    result = runner.invoke(mod1.cli, ["--help"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: hello [OPTIONS]" in result.output
    assert "--name TEXT" in result.output
    assert "Show this message and exit." in result.output
    assert result.exit_code == 0

    result = runner.invoke(mod1.cli, ["--name=Mark"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Hi, Mark!" in result.output
    assert result.exit_code == 0

    result = runner.invoke(mod1.cli, [])
    LOG.debug(result.output)
    assert "Error: Missing option '--name'" in result.output
    assert result.exit_code == 2


def test_simple_command_help(runner: CliRunner):
    result = runner.invoke(mod2.cli, ["--help"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: hello [OPTIONS]" in result.output
    assert "--name TEXT" in result.output
    assert "How I should call you" in result.output
    assert "Show this message and exit." in result.output
    assert result.exit_code == 0

    result = runner.invoke(mod2.cli, ["--name=Mark"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Oh, hi Mark!" in result.output
    assert result.exit_code == 0

    result = runner.invoke(mod2.cli, [])
    LOG.debug(result.output)
    assert "Error: Missing option '--name'" in result.output
    assert result.exit_code == 2


def test_simple_command_default(runner: CliRunner):
    result = runner.invoke(mod3.cli, ["--help"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: hello [OPTIONS]" in result.output
    assert "--name TEXT" in result.output
    assert "How I should call you" in result.output
    assert "Show this message and exit." in result.output
    assert result.exit_code == 0

    result = runner.invoke(mod3.cli, ["--name=Paul"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Oh, hi Paul!" in result.output
    assert result.exit_code == 0

    result = runner.invoke(mod3.cli, [])
    LOG.debug(result.output)
    assert not result.exception
    assert "Oh, hi Mark!" in result.output
    assert result.exit_code == 0


def test_script_command():
    result = subprocess.run(
        ["coverage", "run", mod1.__file__, "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    assert "Usage:" in result.stdout


def test_script_description():
    result = subprocess.run(
        ["coverage", "run", mod2.__file__, "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    assert "Usage:" in result.stdout
    assert "How I should call you" in result.stdout


def test_script_default():
    result = subprocess.run(
        ["coverage", "run", mod3.__file__, "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    assert "Usage:" in result.stdout
    assert "How I should call you" in result.stdout
