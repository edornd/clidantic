# Help and Defaults

## The _help_ directive
As in every command line interface, before any actual command is executed it is often required to consult the _help_.
As usual, to print the available commands and their options it is sufficient to execute the command with the `--help/-h` option.
For instance, a script like the following:
```python title="main.py" linenums="1"
{!examples/simple/simple_cmd.py!}
```
Will provide the following output:
```console
$ python main.py --help
> Usage: main.py [OPTIONS]
>
> Options:
>   --name TEXT  [required]
>   --help       Show this message and exit.
```

As you can notice, every field from the configuration model parsed by the command is converted into a _click_ option and displayed in the `help`.
Each field has a name, a type, an optional _required_ flag and its description.
In this specific example, the description is present for the _help_ command only, while the name is missing one.

## Adding descriptions

Defining configurations through types only does not allow for descriptive definitions.
Pydantic allows for field descriptions through the `Field` class:

```python title="main.py" linenums="1" hl_lines="9"
{!examples/simple/simple_help.py!}
```
This will allow fields to have more details in the _help_ output:
```console
$ python main.py --help
> Usage: main.py [OPTIONS]
>
> Options:
>  --name TEXT  How I should call you  [required]
>  --help       Show this message and exit.
```
## Default values
Models support default values by simply assigning them to the field:

```python
class Config(BaseModel):
    name: str = "Mark"
    age: int = 42
```

It is also possible to combine default values and descriptions through the `Field` class, for instance:

```python title="main.py" linenums="1"  hl_lines="9"
{!examples/simple/simple_default.py!}
```

When executed, this script will result in:
```console
$ python main.py --help
> Usage: main.py [OPTIONS]
>
> Options:
> --name TEXT  How I should call you  [default: Mark]
> --help       Show this message and exit.
```
Informing the user that the `name` field is not strictly required, and in case it is not provided it will assume the value `Mark`.