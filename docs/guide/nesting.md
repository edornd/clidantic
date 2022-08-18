# Nested Commands

Probably the most important _click_ feature is represented by _command groups_, where commands can be nested to create
an interface with multiple commands.
The following sections provide a detailed view on how this functionality is supported in _clidantic_.

## The Parser class
Command groups are natively supported in _clidantic_ through the `Parser` class: each _Parser_ acts seamlessly either
as command when only one is available, or as a group of commands when more than one is added to it.
The following CLI only contains one command:
```python title="single.py" linenums="1" hl_lines="13"
from pydantic import BaseModel
from clidantic import Parser


class Item(BaseModel):
    name: str
    price: float = 0.0


cli = Parser(name="items")


@cli.command()
def buy(item: Item):
    print(f"Bought {item.name} for ${item.price:.2f}")


if __name__ == "__main__":
    cli()
```
When executing the help, since there's no other option, _clidantic_ immediately shows the help for the `buy` command,
thus acting as a single _click_ `Command`:
```console
$ python single.py --help
> Usage: single.py [OPTIONS]
>
> Options:
>   --name TEXT    [required]
>   --price FLOAT  [default: 0.0]
>   --help         Show this message and exit.
```

Parsers can handle a list of commands without explicit nesting, internally creating a _click_ group.
When there is more than one choice, the function name is necessary to execute the correct command.
For instance, with two commands:

```python title="multi.py" linenums="1" hl_lines="13 18"
from pydantic import BaseModel
from clidantic import Parser


class Item(BaseModel):
    name: str
    price: float = 0.0


cli = Parser(name="items")


@cli.command()
def buy(item: Item):
    print(f"Bought {item.name} for ${item.price:.2f}")


@cli.command()
def sell(item: Item):
    print(f"Sold {item.name} for ${item.price:.2f}")


if __name__ == "__main__":
    cli()
```

The help will provide the following information:
```console
$ python multi.py --help
> Usage: multi.py [OPTIONS] COMMAND [ARGS]...
>
> Options:
>   --help  Show this message and exit.
>
> Commands:
>   buy
>   sell
```

The input description for the required fields will only be provided on the help of the specific command itself.
Of course, input parameters are provided _after_ the command name:
```console
$ python multi.py buy --help
> Usage: multi.py buy [OPTIONS]
>
> Options:
>   --name TEXT    [required]
>   --price FLOAT  [default: 0.0]
>   --help         Show this message and exit.

$ python multi.py buy --name bananas --price 2.0
> Bought bananas for $2.00
```

!!! warning

    The support for groups and nested commands is still quite minimal at this point. For instance, commands and groups
    are still missing description options in the help, as well as more advanced functionality.

## Combining multiple parsers

In click, commands and groups can be repeatedly combined and nested to form a tree-like structure of functions.
This is extremely useful to organize more complex tools, imagine something like `git`, which provides multiple complex
sub-commands.

In _clidantic_, this feature is supported through the `Parser.merge` option:

```python title="nested.py" linenums="1" hl_lines="12 13 37"
{!examples/subgroups/nested_simple.py!}
```

In this specific case, every `Parser` instance requires its own name, so that the user can select the right group
during the execution. Of course, the _help_ and command invocation will reflect this command hierachy:

```console
$ python nested.py --help
> Usage: nested.py [OPTIONS] COMMAND [ARGS]...
>
> Options:
>   --help  Show this message and exit.
>
> Commands:
>   items
>   store

$ python nested.py store --help
> Usage: nested.py store [OPTIONS] COMMAND [ARGS]...
>
> Options:
>   --help  Show this message and exit.
>
> Commands:
>   add
>   remove

$ python nested.py store add --help
Usage: nested.py store add [OPTIONS]
>
> Options:
>   --name TEXT    [required]
>   --price FLOAT  [default: 0.0]
>   --help         Show this message and exit.

$ python nested.py store add --name tomatoes --price 4.0
> Added tomatoes to the store
```