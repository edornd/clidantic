# clidantic
Elegant CLIs merging Click and Pydantic
> WARNING: Library in early alpha stage

## Install
The safest path is to install the latest release using pip:
```
pip install clidantic
```
Optionally, you can install the latest updates through GitHub:
```
pip install git+https://github.com/edornd/clidantic.git
```
or, if that doesn't work, with multiple steps (this last step requires poetry to build a setup probably):
```
git clone https://github.com/edornd/clidantic.git
cd clidantic
pip install .
```

# Quickstart
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
