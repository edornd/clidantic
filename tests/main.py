import clidantic as cli
from pydantic import BaseSettings


class TestSettings(BaseSettings):
    food: str
    drink: int
    whatever: bool = None

@cli.group()
def cli_group():
    pass


@cli.command()
@cli.option('--count', default=1, help='Number of greetings.')
@cli.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        cli.echo(f"Hello {name}!")

@cli.config_command(config=TestSettings)
def  goodbye(settings: TestSettings):
    print(str(settings.dict()))


if __name__ == '__main__':
    cli_group.add_command(hello)
    cli_group.add_command(goodbye)
    cli_group()

