import importlib
import typing as types
from enum import Enum

from click import Context, Parameter
from click.types import Choice, ParamType


class JsonType(ParamType):
    name = "json"


class ModuleType(ParamType):
    name = "module"

    def _import_object(self, value: str) -> types.Any:
        module_name, class_name = value.rsplit(".", maxsplit=1)
        assert all(s.isidentifier() for s in module_name.split(".")), f"'{value}' is not a valid module name"
        assert class_name.isidentifier(), f"Variable '{class_name}' is not a valid identifier"

        module = importlib.import_module(module_name)
        if class_name:
            try:
                return getattr(module, class_name)
            except AttributeError:
                raise ImportError(f"Module '{module_name}' does not define a '{class_name}' variable.")
        return None

    def convert(self, value: str, param: types.Optional[Parameter], ctx: types.Optional[Context]) -> types.Any:
        try:
            if isinstance(value, str):
                return self._import_object(value)
            return value
        except Exception as exc:
            self.fail(f"'{value}' is not a valid object ({type(exc)}: {str(exc)})", param, ctx)


class EnumChoice(Choice):
    name = "enum"

    def __init__(self, enum: Enum, case_sensitive: bool = False):
        self.enum = enum
        super().__init__([e.name for e in self.enum], case_sensitive)

    def convert(self, value: types.Any, param: types.Optional[Parameter], ctx: types.Optional[Context]):
        if isinstance(value, self.enum):
            return value
        result = super().convert(value, param, ctx)
        if isinstance(result, str):
            result = self.enum[result]
        return result
