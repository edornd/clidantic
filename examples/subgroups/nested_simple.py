from pydantic import BaseModel

from clidantic import Parser


class Item(BaseModel):
    name: str
    price: float = 0.0


# the name is required for nested CLIs
items = Parser(name="items")
store = Parser(name="store")


@items.command()
def buy(item: Item):
    print(f"Bought {item.name} for ${item.price:.2f}")


@items.command()
def sell(item: Item):
    print(f"Sold {item.name} for ${item.price:.2f}")


@store.command()
def add(item: Item):
    print(f"Added {item.name} to the store")


@store.command()
def remove(item: Item):
    print(f"Removed {item.name} from the store")


# now the command groups can be merged together
cli = Parser.merge(items, store)

if __name__ == "__main__":
    cli()
