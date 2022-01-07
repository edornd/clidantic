from typing import IO, Any, Mapping, Optional, Sequence, Union

from click import testing

from clidantic import Parser


class CliRunner(testing.CliRunner):
    def invoke(
        self,
        cli: Parser,
        args: Optional[Union[str, Sequence[str]]] = None,
        input: Optional[Union[str, bytes, IO]] = None,
        env: Optional[Mapping[str, Optional[str]]] = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: Any,
    ) -> testing.Result:
        cli._update_entrypoint()
        if not cli.entrypoint:
            raise ValueError("CLI without commands")
        return super().invoke(
            cli.entrypoint, args=args, input=input, env=env, catch_exceptions=catch_exceptions, color=color, **extra
        )
