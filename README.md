# clidantic
Typed Command Line Interfaces powered by Click and Pydantic.

> :warning: **Library in early alpha stage**

[![test passing](https://img.shields.io/github/workflow/status/edornd/clidantic/Test)](https://github.com/edornd/clidantic)
[![coverage](https://img.shields.io/codecov/c/github/edornd/clidantic)](https://codecov.io/gh/edornd/clidantic)
[![pypi version](https://img.shields.io/pypi/v/clidantic)](https://pypi.org/project/clidantic/)
[![python versions](https://img.shields.io/pypi/pyversions/clidantic)](https://github.com/edornd/clidantic)

---
## Documentation

The first draft of documentation is available here: [https://edornd.github.io/clidantic/](https://edornd.github.io/clidantic/)

## Installing
The safest path is to install the latest release using pip:
```
pip install clidantic
```
Optionally, you can install the latest updates through GitHub:
```
pip install git+https://github.com/edornd/clidantic.git
```
or, if that doesn't work, with multiple steps (this last step might require [poetry](https://python-poetry.org/)):
```
git clone https://github.com/edornd/clidantic.git
cd clidantic
pip install .
```

## Quickstart
Here's a quick example to get you started:
```python
from typing import Optional
from pydantic import BaseModel

from clidantic import Parser


class Arguments(BaseModel):
    field_a: str
    field_b: int
    field_c: Optional[bool] = False


cli = Parser()


@cli.command()
def main(args: Arguments):
    print(args)


if __name__ == "__main__":
    cli()
```


## Contributing
We are not quite there yet!
