from pydantic import BaseModel, Field

from clidantic import Parser

cli = Parser()


class Config(BaseModel):
    name: str = Field(description="How I should call you, for instance 'General Kenobi'")


@cli.command()
def hello(args: Config):
    print(f"Hello there, {args.name}!")


if __name__ == "__main__":
    cli()
