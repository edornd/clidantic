from pydantic import BaseModel

from clidantic import Parser

cli = Parser()


class Register(BaseModel):
    name: str
    count: int
    amount: float
    paid: bool
    beep_bop: bytes


@cli.command()
def status(register: Register):
    print(f"Register: {register.name}")
    print(f"bills:    {register.count}")
    print(f"amount:   ${register.amount:.2f}")
    status = "closed" if register.paid else "open"
    print(f"status:   {status}")
    print(f"bytes:    {register.beep_bop}")


if __name__ == "__main__":
    cli()
