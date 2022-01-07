from typing import Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

from pydantic import BaseModel

from clidantic import Parser

cli = Parser()


class Model(BaseModel):
    # lists use typed options, called more than once
    # non-typed lists will act as list of strings
    simple_list: list = None
    list_of_ints: List[int] = None
    # unbound tuples work like lists
    # more specific tuples require multi-arg inputs
    simple_tuple: tuple = None
    multi_typed_tuple: Tuple[int, float, str, bool] = None
    # dictionaries are interpreted as JSON strings
    simple_dict: dict = None
    dict_str_float: Dict[str, float] = None
    # sets will also use multiple options, filtering duplicates
    # non-typed sets will behave as string sets
    simple_set: set = None
    set_bytes: Set[bytes] = None
    frozen_set: FrozenSet[int] = None
    # Optional can be added for readability, doesn't affect parsing
    # Everything belonging to iterables adopts multiple options
    # Mappings also supported more thorough validation
    none_or_str: Optional[str] = None
    sequence_of_ints: Sequence[int] = None
    compound: Dict[str, List[Set[int]]] = None
    deque: Deque[int] = None


@cli.command()
def run(items: Model):
    for k, v in items.dict().items():
        print(f"{k:<20s}: {str(v)}")


if __name__ == "__main__":
    cli()
