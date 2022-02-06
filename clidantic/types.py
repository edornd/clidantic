import importlib
import json
from enum import Enum
from typing import Any, Literal, Mapping, Optional

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
        self.mapping = enum
        self.internal_type = enum
        super().__init__([e.name for e in self.mapping], case_sensitive)

    def convert(self, value: Any, param: Optional[Parameter], ctx: Optional[Context]):
        if isinstance(value, self.internal_type):
            return value
        result = super().convert(value, param, ctx)
        if isinstance(result, str):
            result = self.mapping[result]
        return result


class LiteralChoice(EnumChoice):
    name = "literal"

    def __init__(self, enum: Literal, case_sensitive: bool = False):
        # expect every literal value to belong to the same primitive type
        values = list(enum.__args__)
        item_type = type(values[0])
        assert all(isinstance(v, item_type) for v in values), f"Field {enum} contains items of different types"
        self.internal_type = item_type
        self.mapping = {str(v): v for v in values}
        super(EnumChoice, self).__init__(list(self.mapping.keys()), case_sensitive)
