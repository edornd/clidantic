import logging

import click
import pytest
from click.testing import CliRunner

from clidantic import Parser

LOG = logging.getLogger(__name__)


def test_repr():
    cli = Parser()

    @cli.command()
    def command1():
        pass

    @cli.command()
    def command2():
        pass

    LOG.debug(str(command1))
    LOG.debug(str(command2))
    LOG.debug(str(cli))
    assert cli.entrypoint is None
    assert isinstance(cli.commands, list)
    assert len(cli.commands) == 2
    assert isinstance(cli.subgroups, list)
    assert len(cli.subgroups) == 0
    assert repr(command1) == "<Command command1>"
    assert repr(command2) == "<Command command2>"
    assert repr(cli) == "<CLI None>"


def test_repr_named():
    cli = Parser(name="myCLI")

    @cli.command(name="cmd1")
    def command1():
        pass

    @cli.command(name="cmd2")
    def command2():
        pass

    LOG.debug(str(command1))
    LOG.debug(str(command2))
    LOG.debug(str(cli))
    assert cli.entrypoint is None
    assert isinstance(cli.commands, list)
    assert len(cli.commands) == 2
    assert isinstance(cli.subgroups, list)
    assert len(cli.subgroups) == 0
    assert repr(command1) == "<Command cmd1>"
    assert repr(command2) == "<Command cmd2>"
    assert repr(cli) == "<CLI myCLI>"


def test_entrypoint():
    cli = Parser()

    @cli.command()
    def command1():
        pass

    @cli.command()
    def command2():
        pass

    LOG.debug(str(command1))
    LOG.debug(str(command2))
    LOG.debug(str(cli))
    assert cli.entrypoint is None
    assert isinstance(cli.commands, list)
    assert len(cli.commands) == 2
    assert isinstance(cli.subgroups, list)
    assert len(cli.subgroups) == 0

    cli._update_entrypoint()
    assert cli.entrypoint is not None
    assert isinstance(cli.entrypoint, click.Group)
    LOG.debug(str(cli.entrypoint))


def test_merging_structure():
    cli1 = Parser()
    cli2 = Parser()

    @cli1.command()
    def command1():
        pass

    @cli2.command()
    def command2():
        pass

    # should not be able to merge without a name
    with pytest.raises(AssertionError):
        Parser.merge(cli1, cli2)
    cli1.name = "cli1"
    cli2.name = "cli2"
    cli = Parser.merge(cli1, cli2)
    LOG.debug(str(cli1))
    LOG.debug(str(cli2))
    LOG.debug(str(cli))
    # check structure
    assert cli.entrypoint is None
    assert isinstance(cli.commands, list)
    assert isinstance(cli.subgroups, list)
    assert len(cli.commands) == 0
    assert len(cli.subgroups) == 2
    cli._update_entrypoint()
    assert cli.entrypoint is not None
    assert isinstance(cli.entrypoint, click.Group)


def test_merging_help(runner: CliRunner):
    cli1 = Parser(name="cli1")
    cli2 = Parser(name="cli2")

    @cli1.command()
    def command1():
        pass

    @cli2.command()
    def command2():
        pass

    cli = Parser.merge(cli1, cli2)
    # check help execution
    result = runner.invoke(cli, ["--help"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: root [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "Options:" in result.output
    assert "--help  Show this message and exit." in result.output
    assert "Commands:" in result.output
    assert "cli1" in result.output
    assert "cli2" in result.output
    assert result.exit_code == 0


def test_merging_empty(runner: CliRunner):
    cli1 = Parser(name="cli1")
    cli2 = Parser(name="cli2")

    cli = Parser.merge(cli1, cli2)
    # check help execution
    with pytest.raises(ValueError):
        runner.invoke(cli, ["--help"])
    # and standard execution
    with pytest.raises(ValueError):
        runner.invoke(cli, [])


def test_merging_run(runner: CliRunner):
    cli1 = Parser(name="cli1")
    cli2 = Parser(name="cli2")

    @cli1.command()
    def command1():
        print("hello")

    @cli2.command()
    def command2():
        print("world")

    cli = Parser.merge(cli1, cli2)
    # check no args execution
    result = runner.invoke(cli, [])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: root [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "Commands:" in result.output
    assert "cli1" in result.output
    assert "cli2" in result.output
    assert result.exit_code == 0
    # check cli1
    result = runner.invoke(cli, ["cli1"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: root cli1 [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "Commands:" in result.output
    assert "command1" in result.output
    # check cli2
    result = runner.invoke(cli, ["cli2"])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: root cli2 [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "Commands:" in result.output
    assert "command2" in result.output
    # run both commands
    result = runner.invoke(cli, ["cli1", "command1"])
    LOG.debug(result.output)
    assert not result.exception
    assert "hello" in result.output
    result = runner.invoke(cli, ["cli2", "command2"])
    LOG.debug(result.output)
    assert not result.exception
    assert "world" in result.output


def test_merging_named():
    cli1 = Parser(name="subgroup1")
    cli2 = Parser(name="subgroup2")

    @cli1.command()
    def command1():
        pass

    @cli2.command()
    def command2():
        pass

    cli = Parser.merge(cli1, cli2, name="myCLI")
    LOG.debug(str(cli1))
    LOG.debug(str(cli2))
    LOG.debug(str(cli))

    assert repr(cli1) == "<CLI subgroup1>"
    assert repr(cli2) == "<CLI subgroup2>"
    assert repr(cli) == "<CLI myCLI>"

    assert cli.entrypoint is None
    assert isinstance(cli.commands, list)
    assert isinstance(cli.subgroups, list)
    assert len(cli.commands) == 0
    assert len(cli.subgroups) == 2
    cli._update_entrypoint()
    assert cli.entrypoint is not None
    assert isinstance(cli.entrypoint, click.Group)
    LOG.debug(str(cli.entrypoint))


def test_merging_nested(runner: CliRunner):
    manage_cli = Parser(name="manage")
    signup_cli = Parser(name="signup")
    items_cli = Parser(name="items")

    @manage_cli.command()
    def name():
        pass

    @manage_cli.command()
    def passwd():
        pass

    @signup_cli.command()
    def verify():
        pass

    @items_cli.command()
    def buy():
        pass

    @items_cli.command()
    def sell():
        pass

    users_cli = Parser.merge(signup_cli, manage_cli, name="users")
    cli = Parser.merge(users_cli, items_cli, name="main")
    LOG.debug(str(users_cli))
    LOG.debug(str(items_cli))
    LOG.debug(str(cli))
    # check structure
    assert len(users_cli.commands) == 0
    assert len(users_cli.subgroups) == 2
    assert len(items_cli.commands) == 2
    assert len(items_cli.subgroups) == 0
    assert len(cli.commands) == 0
    assert len(cli.subgroups) == 2
    cli._update_entrypoint()
    assert cli.entrypoint is not None
    assert isinstance(cli.entrypoint, click.Group)
    LOG.debug(str(cli.entrypoint))
    # execute, we first expect the help
    result = runner.invoke(cli, [])
    LOG.debug(result.output)
    assert not result.exception
    assert "Usage: main [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "--help  Show this message and exit." in result.output
    assert "Commands:" in result.output
    assert "items" in result.output
    assert "users" in result.output
    # execute items, expecting two subcommands
    result = runner.invoke(cli, ["items"])
    assert not result.exception
    assert "buy" in result.output
    assert "sell" in result.output
    # execute users, expecting two sub-CLIs
    result = runner.invoke(cli, ["users"])
    assert not result.exception
    assert "signup" in result.output
    assert "manage" in result.output
    # execute signup, expecting a single command
    result = runner.invoke(cli, ["users", "signup"])
    assert not result.exception
    assert "verify" in result.output
    # execute manage, expecting two commands
    result = runner.invoke(cli, ["users", "manage"])
    assert not result.exception
    assert "name" in result.output
    assert "passwd" in result.output
