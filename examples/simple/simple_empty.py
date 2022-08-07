from pydantic import BaseModel

from clidantic import Parser

cli = Parser()


@cli.command()
def function():
    print("Hello world!")


if __name__ == "__main__":
    cli()
