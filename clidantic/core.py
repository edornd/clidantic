import inspect
from functools import update_wrapper
from typing import Any, Callable, List, Optional, Tuple, Type, Union

import click
from pydantic import BaseModel
from pydantic.utils import lenient_issubclass

from clidantic.convert import kwargs_to_settings, settings_to_options


def create_callback(callback: Callable, config_class: Type[BaseModel], internal_delimiter: str) -> Callable:
    def wrapper(**kwargs: Any) -> Any:
        raw_config = kwargs_to_settings(kwargs, internal_delimiter)
        instance = config_class(**raw_config)
        return callback(instance)

    update_wrapper(wrapper, callback)
    return wrapper


class Parser:
    def __init__(self, name: str = None, subgroups: List["Parser"] = []) -> None:
        self.name = name
        self.entrypoint: Callable = None
        self.subgroups: List["Parser"] = list(subgroups)
        self.commands: List[click.Command] = []

    def __call__(self) -> Any:
        self._update_entrypoint()
        if not self.entrypoint:
            raise ValueError("CLI not initialized")
        return self.entrypoint()

    def _group_commands(
        self, force_group: bool = False, create_empty: bool = False
    ) -> Union[click.Command, click.Group]:
        if not self.commands:
            if not create_empty:
                return None
            else:
                return click.Group(name=self.name)
        if len(self.commands) == 1 and not force_group:
            return self.commands[0]
        return click.Group(name=self.name, commands=self.commands)

    def _update_entrypoint(self, force_group: bool = False) -> None:
        if self.subgroups:
            # first, update sub-clis to get an entrypoint
            for cli in self.subgroups:
                cli._update_entrypoint(force_group=True)
            main = self._group_commands(force_group=True, create_empty=True)
            for cli in self.subgroups:
                main.add_command(cli.entrypoint)
            self.entrypoint = main
        elif self.commands:
            self.entrypoint = self._group_commands(force_group=force_group)

    def command(
        self,
        name: Optional[str] = None,
        command_class: Optional[Type[click.Command]] = click.Command,
        delimiter: str = ".",
        internal_delimiter: str = "__",
    ) -> Callable:
        assert (
            internal_delimiter.isidentifier()
        ), f"The internal delimiter {internal_delimiter} is not a valid identifier"

        def decorator(f: Callable) -> click.Command:
            # create a name or use the provided one
            command_name = name or f.__name__.lower().replace("_", "-")
            # convert parameters
            func_params = inspect.signature(f).parameters
            if func_params:
                assert len(func_params) == 1, "Multi-configuration commands not supported yet"
                _, cfg_param = next(iter(func_params.items()))
                cfg_class = cfg_param.annotation
                assert lenient_issubclass(cfg_class, BaseModel), "Configuration must be a pydantic model"
                # build param list
                params: List[click.Parameter] = list(settings_to_options(cfg_class, delimiter, internal_delimiter))
                # create command with callback
                command = command_class(
                    name=command_name, callback=create_callback(f, cfg_class, internal_delimiter), params=params
                )
            else:
                # also handle empty commands
                command = command_class(name=command_name, callback=f, params=[])

            # add command to current CLI list
            self.commands.append(command)
            # return command
            return command

        return decorator

    @classmethod
    def merge(cls, *subgroups: Tuple["Parser", ...], name: Optional[str] = None) -> "Parser":
        return cls(name=name, subgroups=subgroups)
