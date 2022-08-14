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
