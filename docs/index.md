# Clidantic

*Typed Command Line Interfaces powered by [Click](https://github.com/pallets/click) and [Pydantic](https://github.com/samuelcolvin/pydantic).*

Clidantic tries to bridge the powerful typed data management provided by *pydantic* with the composability offered by *click*.

## Quickstart
To install, simply run:
```bash
pip install clidantic
```
As you guessed, there are only two major dependencies, _pydantic_ and _click_.

Once the package is installed, you can create a CLI using _pydantic_ models or configurations.

```python
from pydantic import BaseModel
from clidantic import Parser

# create your CLI params as a model
class Arguments(BaseModel):
    field_a: str
    field_b: int
    field_c: bool = False


# instantiate the CLI runner
cli = Parser()

# decorate functions with your models as input
# to use it as CLI command
@cli.command()
def main(args: Arguments):
    print(args)


# last, simply execute your CLI
if __name__ == "__main__":
    cli()
```

## Features
**Typed declarations**

CLI arguments are declared using _pydantic_ models in plain Python code, without the need for string-based argument declarations such as _argparse_, or even vanilla _click_.

**IDE-friendly**

Models are standard Python classes with annotated arguments. Auto-completion, linting and other IDE features should all work as expected, without the need to guess argument names.

**Validation by default**

Using _pydantic_ definitions, *clidantic* inherently leverages on its powerful validation features.

**Modularity**

Clidantic offers full control over the CLI, with composable commands, and composable models: input configurations are as simple as plain models, this means that every validation capability, including custom validators, apply here.

## Acknowledgements

Clidantic is by no means an original idea: the project is a condensed and pratical version of ideas originated from this
[original discussion](https://github.com/samuelcolvin/pydantic/issues/756#issuecomment-798779264).
Special thanks to `@frederikaalund` and the [`cyto`](https://github.com/sbtinstruments/cyto) library for comments and example code.

## Contributions

Clidantic is in early development stage, but if you feel this project deserves more love, you're welcome!
Feel free to suggest new features and changes on GitHub.
