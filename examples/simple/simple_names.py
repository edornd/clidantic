from pydantic import BaseModel

from clidantic import Parser
from clidantic.fields import CLIField

cli = Parser()


class Config(BaseModel):
    name: str = CLIField("-n", "--nombre", default="Mark", description="How I should call you")


@cli.command()
def hello(args: Config):
    """Greets the user with the given name"""
    print(f"Oh, hi {args.name}!")


if __name__ == "__main__":
    cli()
