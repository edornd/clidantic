from pydantic import BaseModel, BaseSettings

from clidantic import Cli


class Complex(BaseModel):
    value_a: float = 0.1
    value_b: str = "hola"


class TrainConfig(BaseSettings):
    batch_size: int = 512
    amp: bool = True


cli1 = Cli(name="welcome")
cli2 = Cli(name="ml")


@cli1.command()
def hello(model: Complex):
    print("we are in function!")
    print(model)


@cli1.command()
def hola(model: Complex):
    print("estamos in hola!")
    print(model)


@cli2.command()
def train(cfg: TrainConfig):
    print(cfg)


cli = Cli.merge(cli1, cli2, name="master")


if __name__ == "__main__":
    cli()
