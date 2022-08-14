# Introduction

## Parsers
The main building block of *clidantic* is represented by a `Parser` instance.
Every CLI requires at least one active parser, which serves as main entry point.
A parser simply acts as a collection of commands and arguments, which are only executed upon call.

 Any `Parser` must first be imported, instantiated, then called in a main, like so:

```python title="main.py" linenums="1" hl_lines="3 5 9"
{!examples/simple/simple_uninit.py!}
```
However, **this code is not enough to have a working CLI**. If you attempt to run it you will obtain:
```console
$ python main.py
> ValueError: CLI not initialized
```
This is expected, it lacks any functionality, which is provided by *commands* and their arguments.

## Commands

In order for a CLI to be ready for execution, it needs to know what to do: this information is provided
through the *command* decorator. The following is the simplest *working* possible interface, which simply executes
a function with a single print and exits (albeit without errors this time).

```python title="main.py" linenums="1" hl_lines="8"
{!examples/simple/simple_empty.py!}
```

```console
$ python main.py
> Hello world!
```
We are getting there, but the command function lacks *arguments*.

## Command arguments

At the base of any command-line interface there is a pydantic `BaseModel`.
Simply put, a *model* is a special Python class defining the structure of a single entity
with its set of fields and their type.

Each model field represents an input argument, whose appearance in the command line interface is dictated
by its type and its options. For instance, a simple command with one argument, requires a model with
one field:

```python title="main.py" linenums="1" hl_lines="8 9 13"
{!examples/simple/simple_cmd.py!}
```

## CLI execution

Models are automatically parsed into click *options* and associated with the decorated function.
The available commands and their arguments can be inspected with the classical `--help` page:

```console
$ python main.py --help
> Usage: main.py [OPTIONS]
>
> Options:
>   --name TEXT  [required]
>   --help       Show this message and exit.
```
This informs us that the command requires options, specifically a `name` string, and of course the `help` directive.
So, let's provide a name:

```console
$ python main.py --name Mark
> Hi, Mark!
```
Since you have a keen eye, you probably noticed that the option is marked as `required`.
That's because we did not specify anything else to the model's `name` field, except for its type.
Following *pydantic*'s logic, such field thus is handled as a *required option* by *click* as well:

```console
$ python main.py
> Usage: main.py [OPTIONS]
> Try 'main.py --help' for help.
>
> Error: Missing option '--name'.
```

Later sections will provide more detail on optional and more complex arguments.
In summary, *clidantic* requires three main ingredients:

- **A function** to be executed, very much like a *click* `Command`.
- **A set of arguments**, provided by a *pydantic* `BaseModel`.
- A `Parser` instance, that provides the glue between the arguments to the commands.

