from enum import Enum, IntEnum
from typing import Literal

from pydantic import BaseModel

from clidantic import Parser

cli = Parser()


class ToolEnum(Enum):
    hammer = "Hammer"
    screwdriver = "Screwdriver"


class HTTPEnum(IntEnum):
    ok = 200
    not_found = 404
    interal_error = 500


class Settings(BaseModel):
    a: Literal["one", "two"]
    b: Literal[1, 2] = 2
    c: Literal[True, False]
    d: ToolEnum
    e: HTTPEnum = HTTPEnum.not_found


@cli.command()
def run(settings: Settings):
    for k, v in settings.dict().items():
        print(f"{k:<20s}: {str(v)}")


if __name__ == "__main__":
    cli()
