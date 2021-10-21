import importlib
import inspect
import json
import typing as types
from enum import Enum

from pydantic import BaseModel
from pydantic.types import Json, JsonWrapper
from pydantic.utils import lenient_issubclass

from click import ParamType

from clidantic.types import JSON_TYPE, MODULE_TYPE, EnumChoice

SingleClickParamType = types.Union[type, ParamType]
ClickParamType = types.Union[SingleClickParamType, types.Tuple[SingleClickParamType, ...]]


def clickify_type(click_type: type) -> ClickParamType:
    # E.g.: Json, Json[List[str]], etc.
    # Return `str` since pydantic will parse the JSON in a later step
    if lenient_issubclass(click_type, Enum):
        return EnumChoice(enum=click_type)
    if is_typing(click_type):
        return MODULE_TYPE
    if lenient_issubclass(click_type, (Json, JsonWrapper)):
        return JSON_TYPE
    if is_mapping(click_type):
        return JSON_TYPE
    # E.g.: list, FrozenSet[int], Tuple[int, ...], etc.
    if is_container(click_type):
        return _clickify_container_args(click_type)
    # E.g.: int, str, float, etc.
    return click_type


def clickify_default(default: types.Any, click_type: type) -> types.Any:
    # Pydantic uses both `None` and `Ellipsis` to denote "no default value".
    # Click only understands `None`, so we return that.
    if default in (None, Ellipsis):
        return None
    if lenient_issubclass(click_type, Enum):
        return default.name
    if is_typing(click_type):
        module_name = inspect.getmodule(default).__name__
        return f"{module_name}.{default.__name__}"
    # Early out if the user explicitly forces the field type to JSON
    if is_mapping(click_type):
        return json.dumps(default)
    if is_container(click_type):
        return _clickify_container_default(default)
    return default


def get_show_default(default: types.Any, type_: type) -> types.Union[bool, str]:
    # click's help message for an empty container is "[default: ]". This can
    # confuse the user user. Therefore, we explicitly set the `show_default`
    # to, e.g., "empty list". In turn, click displays this as
    # "[default: (empty list)]". Note that click adds the parentheses.
    if is_container(type_) and not default:
        name = _type_name(type_)
        return f"empty {name}"
    # For non-containers, we always show the default. We simply return `True` so
    # that click automatically figures out a proper default text.
    return True


def get_multiple(type_: type) -> bool:
    # Early out for mappings. E.g., dict.
    if is_mapping(type_):
        return False
    # For containers, we allow multiple arguments. This way, the user
    # can specify an option multiple times and click gathers all values
    # into a single container. E.g.:
    #   $ python app.py --lucky-numbers 2 --lucky-numbers 7
    # becomes
    #   `{ "lucky_numbers": [2, 7] }`.
    if is_container(type_):
        args = _clickify_container_args(type_)
        # A non-composite type has a single argument.
        # E.g., `List[int]`.
        # A composite type has a tuple of arguments.
        # E.g., `Tuple[str, int, int]`.
        composite = isinstance(args, tuple)
        # We only allow the user to specify multiple values for non-composite types.
        # E.g., for `list`, `Tuple[str, ...]`, `FrozenSet[int]`, etc.
        return not composite
    return False


def is_mapping(type_: type) -> bool:
    # Early out for standard containers. E.g., dict, OrderedDict
    if lenient_issubclass(type_, types.Mapping):
        return True
    origin = types.get_origin(type_)
    # Early out for non-typing objects
    if origin is None:
        return False
    return issubclass(origin, types.Mapping)


def is_container(type_: type) -> bool:
    # Early out for `str`. While `str` is technically a container, it's easier to
    # not consider it one in the context of command line interfaces.
    if type_ is str:
        return False
    # Early out for standard containers. E.g.: list, tuple, range
    if lenient_issubclass(type_, types.Container):
        return True
    origin = types.get_origin(type_)
    # Early out for non-typing objects
    if origin is None:
        return False
    return issubclass(origin, types.Container)


def is_typing(field_type: type) -> bool:
    raw = types.get_origin(field_type)
    if raw is None:
        return False
    if raw is type or raw is types.Type:
        return True
    return False


def _clickify_container_args(type_: type,) -> ClickParamType:
    assert is_container(type_)
    args: types.Tuple[types.Any, ...] = types.get_args(type_)
    # Early out for untyped containers such as `tuple`, `List[Any]`, `frozenset`, etc.
    if len(args) == 0:
        # When we don't know the type, we choose `str`. It's tempting to choose `None`
        # but that invokes click's type-guessing logic. We don't want to do that since
        # it often incorrectly guesses that we want a composite type when we don't. [2]
        return str
    # Early out for homogenous containers (contains items of a single type)
    if len(args) == 1:
        return _clickify_arg(args[0])
    # Early out for homogenous tuples of indefinite length. E.g., `Tuple[int, ...]`.
    if len(args) == 2 and args[1] is Ellipsis:
        return _clickify_arg(args[0])
    # Last case is fixed-length containers (contains a fixed number of items of a
    # given type). E.g., `Tuple[str, int, int]`.
    return tuple(_clickify_args(args))


def _clickify_args(args: types.Tuple[type, ...],) -> types.Iterable[SingleClickParamType]:
    return (_clickify_arg(arg) for arg in args)


def _clickify_arg(arg: type) -> SingleClickParamType:
    # When we don't know the type, we choose `str` (see [2])
    if arg is types.Any:
        return str
    # For containers and nested models, we use JSON
    if is_container(arg) or issubclass(arg, BaseModel):
        return JSON_TYPE
    return arg


def _clickify_container_default(default: types.Any) -> types.Optional[types.Tuple[types.Any, ...]]:
    assert issubclass(type(default), types.Sequence)
    return tuple(v.json() if isinstance(v, BaseModel) else v for v in default)


def _type_name(type_: type) -> str:
    origin: types.Optional[type] = types.get_origin(type_)
    if origin is None:
        return type_.__name__
    return origin.__name__
