# Advanced Topics

## Setuptools Integration
When distributing a module or a package, it is often better to bundle any command line utility inside the package
itself. There are many reasons for this, as explained by the [click documentation](https://click.palletsprojects.com/en/8.1.x/setuptools/).

The integration simply requires to register the main `cli` instance as console entrypoint in a standard `setup.py` file.
Following the example provided by *click*, we use a directory structure composed of two files:
```
main.py
setup.py
```
The `main.py` script contains a minimal CLI to be executed, for instance:
```python
from clidantic import Parser

cli = Parser()


@cli.command()
def function():
    print("Hello world!")


if __name__ == "__main__":
    cli()
```
Note that the `__main__` block can still kept without issues.
In the `setup.py` script it is now sufficient to indicate the main script as console entrypoint, for instance:

```python
from setuptools import setup

setup(
    name='test-cli',
    version='0.1.0',
    py_modules=['main'],
    install_requires=[
        'clidantic',
    ],
    entry_points={
        'console_scripts': [
            'mycommand = main:cli',
        ],
    },
)
```
In order to execute the main script as part of the package, the module needs to be installed:
```console
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -e .
$ mycommand
> Hello world!
```

This is an absolutely minimal example with unconventional names, just to better highlight which components refer to which part.
Of course, `mycommand` can be customized with a different name and different entrypoints.
Fro more information, check out the [click guide](https://click.palletsprojects.com/en/8.1.x/setuptools/) and the [Python packaging guide](https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point).


# Customizing the help

Currently, there is not much available to customize the help, the only functionality available at this time is the
_maximum content width_.
The default _click_ width is set to 79 characters, while _clidantic_ raises it to 119.
To customize the extents of the help string, it is sufficient to provide the `content_width`
keyword argument when calling the main CLI:

```python title="main.py" linenums="1"  hl_lines="18"
from pydantic import BaseModel, Field
from clidantic import Parser


class Config(BaseModel):
    name: str = Field(alias="n", description="a long sentence that may be wrapped depending on the terminal width")


cli = Parser()


@cli.command()
def main(config: Config):
    print(config)


if __name__ == "__main__":
    cli(content_width=40)
```

Executing this script will provide a shorter help, wrapping longer descriptions on multiple lines:
```console
$ python clid_test.py --help
> Usage: clid_test.py [OPTIONS]
>
> Options:
>   --name TEXT  a long sentence that may be
>                truncated depending on the terminal
>                width  [required]
>   --help       Show this message and exit.
```