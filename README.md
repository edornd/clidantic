# clidantic
Elegant CLIs merging Click and Pydantic
> WARNING: Library in early alpha stage

## Install
You can install this package via pip, getting the latest features through GitHub:
```
pip install git+https://github.com/edornd/clidantic.git
```
Or installing the latest release:
```
pip install clidantic
```

# Quickstart
Here's a quick example:
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
We are not quite there yet :)
