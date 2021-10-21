from collections import defaultdict
from enum import Enum
from functools import partial
from typing import (Any, Callable, DefaultDict, Dict, Iterable, List, Tuple, Type)

from pydantic import BaseModel, BaseSettings
from pydantic.fields import ModelField
from pydantic.utils import lenient_issubclass
from clidantic.click import (clickify_default, clickify_type, get_multiple, get_show_default)

from click import Command, Context, Option, Parameter


class Initializer(partial):
    """Picklable partial version, thanks to the eq implementation.
    """

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, partial):
            return False
        return self.func == o.func and self.args == o.args and self.keywords == o.keywords


class CallableEnum(Enum):

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.value(*args, **kwds)


def allow_if_specified(context: Context, param: Parameter, value: Any) -> Any:
    """Only allow options that the user explicitly specified, so that the pydantic model
    can keep the declared defaults.

    Args:
        context (Context): click Context, not required
        param (Parameter): click parameter
        value (Any): value for the click parameter

    Returns:
        Any: returns value if it has been explicitly defined by the user
    """
    if isinstance(param, PydanticOption):
        return value if param.specified else None
    return value


class PydanticOption(Option):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs, callback=allow_if_specified)
        self.specified = False

    def handle_parse_result(self, context: Any, options: Any, args: Any) -> Any:
        self.specified = self.name in options
        return super().handle_parse_result(context, options, args)

    @classmethod
    def from_field(cls, field: ModelField, params: Tuple[str, str]):
        assert not lenient_issubclass(field.outer_type_, BaseModel)
        click_type = clickify_type(field.outer_type_)
        default_value = clickify_default(field.default, field.outer_type_)
        show_default = get_show_default(field.default, field.outer_type_)
        multiple = get_multiple(field.outer_type_)
        return cls(params,
                   type=click_type,
                   default=default_value,
                   show_default=show_default,
                   multiple=multiple,
                   help=field.field_info.description)


def param_from_field(field: ModelField, kebab_name: str, delimiter: str, internal_delimiter: str,
                     parent_path: Tuple[str, ...]) -> Tuple[str, str]:
    """Generates an equivalent click CLI parameter from the given pydantic field.

    Args:
        field (ModelField): pydantic Field
        kebab_name (str): name already parsed in 'kebab case' (dashes instead of underscore)
        delimiter (str): delimiter to use in the CLI
        internal_delimiter (str): delimiter to use internally
        parent_path (Tuple[str, ...]): path to the parent object

    Returns:
        Tuple[str, str]: internal identifier and CLI option string
    """
    # example.test-attribute
    base_option_name = delimiter.join(parent_path + (kebab_name,))
    full_option_name = f"--{base_option_name}"
    # Early out of non-boolean fields
    if field.outer_type_ is bool:
        full_disable_flag = delimiter.join(parent_path + (f"no-{kebab_name}",))
        full_option_name += f"/--{full_disable_flag}"
    # example.test-attribute -> example__test_attribute
    identifier = base_option_name.replace(delimiter, internal_delimiter).replace("-", "_")
    return identifier, full_option_name


def settings_to_options(model: BaseModel,
                        delimiter: str,
                        internal_delimiter: str,
                        parent_path: Tuple[str, ...] = tuple()) -> Iterable[Option]:
    """Recursively transforms the given model fields into click Options.
    Composite fields will be split into single primitive types with a full identifier.

    Args:
        model (BaseModel): pydantic model definition
        delimiter (str): delimiter to use at cli level
        internal_delimiter (str): delimiter to use to generate internal identifiers
        parent_path (Tuple[str, ...], optional): full path from root to the current model. Defaults to tuple().

    Returns:
        Iterable[Option]: generator of click Options

    Yields:
        Iterator[Iterable[Option]]: a single click Option
    """
    # iterate over fields in the settings
    for field in model.__fields__.values():
        # checks on delimiters to be done
        kebab_name = field.name.replace("_", "-")
        assert internal_delimiter not in kebab_name
        if lenient_issubclass(field.outer_type_, BaseModel):
            yield from settings_to_options(field.outer_type_,
                                           delimiter,
                                           internal_delimiter,
                                           parent_path=parent_path + (kebab_name,))
            continue
        # simple fields
        params = param_from_field(field, kebab_name, delimiter, internal_delimiter, parent_path)
        yield PydanticOption.from_field(field, params)


def kwargs_to_settings(kwargs: Dict[str, Any], internal_delimiter: str) -> Dict[str, Any]:
    """Transforms a flat dictionary of identifiers and values back into a complex object made of nested dictionaries.
    E.g. the following input: `animal__type='dog', animal__name='roger', animal__owner__name='Mark'`
    becomes: `{animal: {name: 'roger', type: 'dog'}, owner: {name: 'Mark'}}`

    Args:
        kwargs (Dict[str, Any]): flat dictionary of available fields
        internal_delimiter (str): delimiter required to split fields

    Returns:
        Dict[str, Any]: nested dictionary of properties to be converted into pydantic models
    """
    result: DefaultDict[str, Any] = defaultdict(dict)
    for name, value in kwargs.items():
        # skip when not set
        if value is None:
            continue
        # split full name into parts
        parts = name.split(internal_delimiter)
        # create nested dicts corresponding to each part
        # test__inner__value -> {test: {inner: value}}
        nested = result
        for part in parts[:-1]:
            nested = nested[part]
        nested[parts[-1]] = value
    return dict(result)


def config_command(config: Type[BaseSettings], delimiter: str = ".", internal_delimiter: str = "__") -> Callable:
    """Decorator that transforms a given function into a click command, using as arguments a pydantic model.

    Args:
        config (Type[BaseSettings]): pydantic settings class type.
        delimiter (str, optional): base delimiter to divide fields (e.g. animal.name). Defaults to ".".
        internal_delimiter (str, optional): delimiter used internally for identifiers. Defaults to "__".

    Returns:
        Callable: decodated function, transformed into a callable command
    """
    assert internal_delimiter.isidentifier(), f"The internal delimiter {internal_delimiter} is not a valid identifier"

    def decorator(f: Callable[..., Any]) -> Command:
        name = f.__name__.lower().replace("_", "-")
        params: List[Parameter] = list(settings_to_options(config, delimiter, internal_delimiter))

        def click_callback(**kwargs: Any) -> None:
            raw_config = kwargs_to_settings(kwargs, internal_delimiter)
            settings = config(**raw_config)
            f(settings)

        command = Command(name=name, callback=click_callback, params=params)
        return command

    return decorator
