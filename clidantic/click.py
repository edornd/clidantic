#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Code originally derived and adapted from:
https://github.com/samuelcolvin/pydantic/issues/756#issuecomment-798779264.
Credits to Frederik Aalund <https://github.com/frederikaalund> for his valuable suggestions.
"""

import inspect
import json
import typing as types
from enum import Enum

from click import ParamType
from pydantic import BaseModel
from pydantic.types import Json, JsonWrapper
from pydantic.utils import lenient_issubclass

from clidantic.types import BytesType, EnumChoice, JsonType, LiteralChoice, ModuleType


def parse_type(field_type: type) -> ParamType:
    """Transforms the pydantic field's type into a click-compatible type.

    Args:
        field_type (type): pydantic field type

    Returns:
        ParamType: click type equivalent
    """
    assert types.get_origin(field_type) is not types.Union, "Unions are not supported"
    # enumeration strings or other Enum derivatives
    if lenient_issubclass(field_type, Enum):
        return EnumChoice(enum=field_type, case_sensitive=True)
    # literals are enum-like with way less functionality
    if is_literal(field_type):
        return LiteralChoice(enum=field_type, case_sensitive=True)
    # modules, classes, functions
    if is_typing(field_type):
        return ModuleType()
    # entire dictionaries:
    # case 1: using pydantic's field, do not convert beforehand
    if lenient_issubclass(field_type, (Json, JsonWrapper)):
        return JsonType(should_load=False)
    # case 2: using a Dict, convert in advance
    if is_mapping(field_type):
        return JsonType()
    # list, List[p], Tuple[p], Set[p] and so on
    if is_container(field_type):
        return parse_container_args(field_type)
    # bytes are not natively supported by click
    if lenient_issubclass(field_type, bytes):
        return BytesType()
    # return the current type: it should be a primitive
    return field_type


def parse_default(default: types.Any, field_type: type) -> types.Any:
    """Converts pydantic defaults into click default types.

    Args:
        default (types.Any): the current field's default value
        field_type (type): the type of the current pydantic field

    Returns:
        types.Any: click-compatible default
    """
    # pydantic uses none and ..., click only supports none
    if default in (None, Ellipsis):
        return None
    # for enums we return the name as default
    if lenient_issubclass(field_type, Enum):
        return default.name
    # for modules and such, the name is returned
    if is_typing(field_type):
        module_name = inspect.getmodule(default).__name__
        return f"{module_name}.{default.__name__}"
    # for dictionary types, the default is transformed into string
    if is_mapping(field_type):
        return json.dumps(default)
    # for container types, the origin is required
    if is_container(field_type):
        return parse_container_default(default)
    return default


def should_show_default(default: types.Any, field_type: type) -> types.Union[bool, str]:
    """Returns an actual default string for containers, or 'true' to forward the default value decision to click.

    Args:
        default (types.Any): default value from pydantic
        field_type (type): pydantic type

    Returns:
        types.Union[bool, str]: string for containers, or true for the rest
    """
    # include an 'empty <type>' instead of blank spots
    if is_container(field_type) and not default:
        name = get_type_name(field_type)
        return f"empty {name}"
    # For non-containers, we always show the default, returning 'True' triggers click.
    return True


def allows_multiple(field_type: type) -> bool:
    """Checks whether the current type allows for multiple arguments to be provided as input or not.
    For containers, it exploits click's support for lists and such to use the same option multiple times
    to create a complex object: `python run.py --subsets train --subsets test`
    # becomes `subsets: ["train", "test"]`.
    Args:
        field_type (type): pydantic type

    Returns:
        bool: true if it's a composite field (lists, containers and so on), false otherwise
    """
    # Early out for mappings, since it's better to deal with them using strings.
    if is_mapping(field_type):
        return False
    # Activate multiple option for (simple) container types
    if is_container(field_type):
        args = parse_container_args(field_type)
        # A non-composite type has a single argument, such as 'List[int]'
        # A composite type has a tuple of arguments, like 'Tuple[str, int, int]'.
        # For the moment, only non-composite types are allowed.
        return not isinstance(args, tuple)
    return False


def is_literal(field_type: type) -> bool:
    """Checks whether the given field type is a Literal type or not.
    Literals are weird: isinstance and subclass do not work, so you compare
    the origin with the Literal declaration itself.

    Args:
        field_type (type): current pydantic type

    Returns:
        bool: true if Literal type, false otherwise
    """
    origin = types.get_origin(field_type)
    return origin is not None and origin is types.Literal


def is_mapping(field_type: type) -> bool:
    """Checks whether this field represents a dictionary or JSON object.

    Args:
        field_type (type): pydantic type

    Returns:
        bool: true when the field is a dict-like object, false otherwise.
    """
    # Early out for standard containers.
    if lenient_issubclass(field_type, types.Mapping):
        return True
    # for everything else or when the typing is more complex, check its origin
    origin = types.get_origin(field_type)
    if origin is None:
        return False
    return lenient_issubclass(origin, types.Mapping)


def is_container(field_type: type) -> bool:
    """Checks whether the current type is a container type ('contains' other types), like
    lists and tuples.

    Args:
        field_type (type): pydantic field type

    Returns:
        bool: true if a container, false otherwise
    """
    # do not consider strings or byte arrays as containers
    if field_type in (str, bytes):
        return False
    # Early out for standard containers: list, tuple, range
    if lenient_issubclass(field_type, types.Container):
        return True
    origin = types.get_origin(field_type)
    # Early out for non-typing objects
    if origin is None:
        return False
    return lenient_issubclass(origin, types.Container)


def is_typing(field_type: type) -> bool:
    """Checks whether the current type is a module-like type.

    Args:
        field_type (type): pydantic field type

    Returns:
        bool: true if the type is itself a type
    """
    raw = types.get_origin(field_type)
    if raw is None:
        return False
    if raw is type or raw is types.Type:
        return True
    return False


def parse_container_args(field_type: type) -> types.Union[ParamType, types.Tuple[ParamType]]:
    """Parses the arguments inside a container type (lists, tuples and so on).

    Args:
        field_type (type): pydantic field type

    Returns:
        types.Union[ParamType, types.Tuple[ParamType]]: single click-compatible type or a tuple
    """
    assert is_container(field_type), "Field type is not a container"
    args = types.get_args(field_type)
    # Early out for untyped containers: standard lists, tuples, List[Any]
    # Use strings when the type is unknown, avoid click's type guessing
    if len(args) == 0:
        return str
    # Early out for homogenous containers: Tuple[int], List[str]
    if len(args) == 1:
        return parse_single_arg(args[0])
    # Early out for homogenous tuples of indefinite length: Tuple[int, ...]
    if len(args) == 2 and args[1] is Ellipsis:
        return parse_single_arg(args[0])
    # Then deal with fixed-length containers: Tuple[str, int, int]
    return tuple(parse_single_arg(arg) for arg in args)


def parse_single_arg(arg: type) -> ParamType:
    """Returns the click-compatible type for container origin types.
    In this case, returns string when it's not inferrable, a JSON for mappings
    and the original type itself in every other case (ints, floats and so on).
    Bytes is a special case, not natively handled by click.

    Args:
        arg (type): single argument

    Returns:
        ParamType: click-compatible type
    """
    # When we don't know the type, we choose 'str'
    if arg is types.Any:
        return str
    # For containers and nested models, we use JSON
    if is_container(arg) or issubclass(arg, BaseModel):
        return JsonType()
    if lenient_issubclass(arg, bytes):
        return BytesType()
    return arg


def parse_container_default(default: types.Any) -> types.Optional[types.Tuple[types.Any, ...]]:
    """Parses the default type of container types.

    Args:
        default (types.Any): default type for a container argument.

    Returns:
        types.Optional[types.Tuple[types.Any, ...]]: JSON version if a pydantic model, else the current default.
    """
    assert issubclass(type(default), types.Sequence)
    return tuple(v.json() if isinstance(v, BaseModel) else v for v in default)


def get_type_name(field_type: type) -> str:
    """Gets the name of the current type, used for modules, functions and such.

    Args:
        field_type (type): field type of type Typing (weird I know)

    Returns:
        str: name of the module or function, or type
    """
    origin: types.Optional[type] = types.get_origin(field_type)
    if origin is None:
        return field_type.__name__
    return origin.__name__
