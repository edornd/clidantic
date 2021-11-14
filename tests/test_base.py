from click.testing import CliRunner

from clidantic import Parser


def test_empty_command(runner: CliRunner):
    cli = Parser()

    @cli.command()
    def empty():
        print("Hello world!")

    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert "Hello world!" in result.output
