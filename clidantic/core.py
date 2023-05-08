import inspect
from functools import update_wrapper
from typing import Any, Callable, List, Optional, Tuple, Type, Union

import click
from pydantic import BaseModel
from pydantic.utils import lenient_issubclass

from clidantic.convert import kwargs_to_settings, settings_to_options


def create_callback(callback: Callable, config_class: Type[BaseModel], internal_delimiter: str) -> Callable:
    """Creates a callback from the actual callback function provided. This serves as middle step to parse
    the configuration and validate inputs before actually passing it to the function.

    Args:
        callback (Callable): function to be called once the configuration is created
        config_class (Type[BaseModel]): target configuration class, used as factory.
        internal_delimiter (str): delimiter used to identify subfields from click.

    Returns:
        Callable: new callback, wrapping the original function to convert click stuff into a configuration.
    """

    def wrapper(**kwargs: Any) -> Any:
        raw_config = kwargs_to_settings(kwargs, internal_delimiter)
        instance = config_class(**raw_config)
        return callback(instance)

    update_wrapper(wrapper, callback)
    return wrapper


class Parser:
    """Creates a new CLI building block.
    A parser allows to create a click command or group and allows for composition.
    """

    def __init__(self, name: str = None, subgroups: List["Parser"] = []) -> None:
        self.name = name
        self.entrypoint: Callable = None
        self.subgroups: List["Parser"] = list(subgroups)
        self.commands: List[click.Command] = []

    def __call__(self, content_width: int = 119) -> Any:
        """Calling the CLI object will initiate the actual argument parsing,
        if an entrypoint has been defined.

        Raises:
            ValueError: when the CLI is not initialized.

        Returns:
            Any: doesn't actually return anything at the moment.
        """
        self._update_entrypoint()
        if not self.entrypoint:
            raise ValueError("CLI not initialized")
        return self.entrypoint(max_content_width=content_width)

    def __repr__(self) -> str:
        return f"<CLI {self.name}>"

    def _group_commands(
        self, force_group: bool = False, create_empty: bool = False
    ) -> Union[click.Command, click.Group]:
        """Creates a group from the current list of commands.
        Also allows for empty or singleton groups, if required for merging.

        Args:
            force_group (bool, optional): Forces the creation of a group, useful for merging. Defaults to False.
            create_empty (bool, optional): Creates a group even with no registered commands. Defaults to False.

        Returns:
            Union[click.Command, click.Group]: returns the created group or a single command.
        """
        if not self.commands:
            if not create_empty:
                return None
            else:
                return click.Group(name=self.name)
        if len(self.commands) == 1 and not force_group:
            return self.commands[0]
        return click.Group(name=self.name, commands=self.commands)

    def _update_entrypoint(self, force_group: bool = False) -> None:
        """Updates the current entrypoint based on the current stored values.
        The function recursively traverses its subtree to initialize the entrypoint of children CLI first.

        Args:
            force_group (bool, optional): Forces group creation on the current Parser. Defaults to False.
        Raises:
            ValueError: when a subgroup is not initialized.
        """
        if self.subgroups:
            # first, update sub-clis to get an entrypoint
            for cli in self.subgroups:
                cli._update_entrypoint(force_group=True)
            main = self._group_commands(force_group=True, create_empty=True)
            # then add the sub-entrypoints to the current main component
            # those are the sub-groups created in the children CLIs
            for cli in self.subgroups:
                if cli.entrypoint is None:
                    raise ValueError(f"Subgroup '{cli.name}' does not have any commands.")
                main.add_command(cli.entrypoint)
            # then update the current entrypoint with the combination
            # of the children.
            self.entrypoint = main
        # when subgroups are not present, check if there are commands and group them.
        # if so, it means we are in a 'leaf' parser, or a one-level parser.
        elif self.commands:
            self.entrypoint = self._group_commands(force_group=force_group)

    def command(
        self,
        name: Optional[str] = None,
        help_message: Optional[str] = None,
        command_class: Optional[Type[click.Command]] = click.Command,
        delimiter: str = ".",
        internal_delimiter: str = "__",
        config_param_name: Optional[str] = None,
    ) -> Callable:
        """Decorator that defines a command function. Commands are just wrappers around click functionalities that use
        Pydantic models as building blocks for options instead of variable arguments.

        Args:
            name (Optional[str], optional): name for the command. When none, the function name is used.
            command_class (Optional[Type[click.Command]], optional): Optional override for the command creation class.
                                                                     Defaults to click.Command.
            delimiter (str, optional): delimiter to be used in the terminal for subfields. Defaults to ".".
            internal_delimiter (str, optional): delimiter used by the parser internally. Defaults to "__".

        Returns:
            Callable: wrapper around the given function that creates a command once called.
        """
        assert (
            internal_delimiter.isidentifier()
        ), f"The internal delimiter {internal_delimiter} is not a valid identifier"

        def decorator(f: Callable) -> click.Command:
            # create a name or use the provided one
            command_name = name or f.__name__.lower().replace("_", "-")
            command_help = help_message or inspect.getdoc(f)
            # extract function parameters and prepare list of click params
            # assign the same function as callback for empty commands
            sig = inspect.signature(f, eval_str=True)
            pass_decorators = []
            params: List[click.Parameter] = []
            callback = f
            config_class = None
            # if we have a configuration, parse it
            # otherwise handle empty commands
            for param_name, param in sig.parameters.items():
                if param.annotation is not param.empty:
                    assert lenient_issubclass(param.annotation, BaseModel), "Configuration must be a pydantic model"
                    if config_param_name and param_name != config_param_name:
                        pass_decorators.append((param.annotation, param_name))
                    else: # old behavior, no config_param_name
                        config_class = param.annotation               
            # create a wrapped callback
            if config_class:
                params = list(settings_to_options(config_class, delimiter, internal_delimiter))
                callback = create_callback(f, config_class=config_class, internal_delimiter=internal_delimiter)

            command = command_class(
                name=command_name,
                callback=callback,
                params=params,
                help=command_help,
            )
            # add command to current CLI list and return it
            self.commands.append(command)
            return command

        return decorator

    @classmethod
    def merge(cls, *subgroups: Tuple["Parser", ...], name: Optional[str] = None) -> "Parser":
        """Class method that merges a variable list of parsers into a single one.

        Args:
            subgroups (Tuple[Parser,...]): variable sequence of CLI blocks (at least 2).
            name (Optional[str], optional): name for the merged group. When none, the default CLI name is used.

        Returns:
            Parser: a new Parser instance with multiple subgroups.
        """
        assert subgroups is not None and len(subgroups) > 1, "Provide at least two Parsers to merge"
        assert all(
            hasattr(cli, "name") and cli.name is not None for cli in subgroups
        ), "Nested parsers must have a name"
        return cls(name=name, subgroups=subgroups)
