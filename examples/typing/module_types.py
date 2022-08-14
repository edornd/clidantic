from typing import Type

from pydantic import BaseModel

from clidantic import Parser


class Optimizer:
    """
    Example of base abstract class
    """


class SGD(Optimizer):
    """
    A specific optimizer implementation
    """


class Adam(Optimizer):
    """
    Another specific optimizer implementation
    """


class Settings(BaseModel):
    field: Type[Optimizer] = SGD


cli = Parser()


@cli.command()
def run(config: Settings):
    print(config.field)


if __name__ == "__main__":
    cli()
