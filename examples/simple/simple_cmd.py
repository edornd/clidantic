from pydantic import BaseModel

from clidantic import Parser

cli = Parser()


class Config(BaseModel):
    name: str


@cli.command()
def hello(args: Config):
    print(f"Hello there, {args.name}!")


if __name__ == "__main__":
    cli()
