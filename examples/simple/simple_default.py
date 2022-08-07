from pydantic import BaseModel, Field

from clidantic import Parser

cli = Parser()


class Config(BaseModel):
    name: str = Field("Mark", description="How I should call you")


@cli.command()
def hello(args: Config):
    print(f"Oh, hi {args.name}!")


if __name__ == "__main__":
    cli()
