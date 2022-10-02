# Customization

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

## Command descriptions

Likewise, it is also possible to provide a description to the command itself to be shown in as additional information
in the help content. Following _click_, this is as simple as inserting _docstrings_ under the decorated function:

```python title="main.py" linenums="1"  hl_lines="14"
{!examples/simple/simple_desc.py!}
```
Executing the `help` command will result in:

```console  hl_lines="4"
$ python main.py --help
> Usage: main.py [OPTIONS]
>
>   Greets the user with the given name
>
> Options:
>   --name TEXT  How I should call you  [required]
>   --help       Show this message and exit.
```

## Additional names and aliases
Option names, especially in heavily nested models, can become difficult to type.
As common practice in command line tools, _clidantic_ offers the possibility to add additional names to each field.
This feature is allowed by the custom `CLIField` operator:

```python title="main.py" linenums="1"  hl_lines="10"
{!examples/simple/simple_names.py!}
```

In this case, the output of the `help` command will be the following:

```console  hl_lines="7"
$ python main.py --help
> Usage: main.py [OPTIONS]
>
>   Greets the user with the given name
>
> Options:
>   -n, --name, --nombre TEXT  How I should call you  [default: Mark]
>   --help                     Show this message and exit.
```

In the example, you may have noticed a few things:
- `CLIField` is _not_ part of _pydantic_, it is a customized version present in _clidantic_.
- The `default` argument has become a *kwarg*, instead of being the first positional argument.
- The new field takes as first (optional) arguments a variable list of additional names for the field.

Aside from these differences, the `CLIField` operator directly mirrors the standard `Field` functionality, therefore
any other input or mechanism can be effectively used, see the `description` argument for instance.


!!! warning

    When using optional names, keep in mind that the **uniqueness is not verified**, and nested models
    will not affect the result. In practice, fields such as `main.subfield-a`, if renamed `sa` will not
    need the `main.` prefix. However, this can be done manually. Consider this when providing additional names.
