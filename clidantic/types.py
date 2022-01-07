import importlib
import json
from enum import Enum
from typing import Any, Mapping, Optional

from click import Context, Parameter
from click.types import Choice, ParamType


class BytesType(ParamType):
    name = "bytes"

    def convert(self, value: Any, param: Optional[Parameter], ctx: Optional[Context]) -> Any:
        if isinstance(value, bytes):
            return value
        try:
            return str.encode(value)
        except Exception as exc:
            self.fail(f"'{value}' is not a valid string ({str(exc)})", param, ctx)


class JsonType(ParamType):
    name = "json"

    def __init__(self, should_load: Optional[bool] = True) -> None:
        super().__init__()
        self.should_load = should_load

    def convert(self, value: Any, param: Optional[Parameter], ctx: Optional[Context]) -> Any:
        if isinstance(value, Mapping) or not self.should_load:
            return value
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            self.fail(f"'{value}' is not a valid JSON string ({str(exc)})", param, ctx)


class ModuleType(ParamType):
    name = "module"

    def _import_object(self, value: str) -> Any:
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

    def convert(self, value: str, param: Optional[Parameter], ctx: Optional[Context]) -> Any:
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

    def convert(self, value: Any, param: Optional[Parameter], ctx: Optional[Context]):
        if isinstance(value, self.enum):
            return value
        result = super().convert(value, param, ctx)
        if isinstance(result, str):
            result = self.enum[result]
        return result
