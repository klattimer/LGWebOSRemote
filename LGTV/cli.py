import logging
import sys
from typing import List, Optional

import click

from LGTV import cli_static
from LGTV.conf import read_config


class CLI(click.MultiCommand):
    def list_commands(self, ctx: click.Context) -> List[str]:
        commands = []

        for command in cli_static.__all__:
            commands.append(command.replace("_", "-"))

        return sorted(commands)

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        fun_name = cmd_name.replace("-", "_")

        if fun_name in cli_static.__all__:
            return getattr(cli_static, fun_name)


@click.group(cls=CLI)
@click.option("-d", "--debug", is_flag=True, help="Enable debug output.")
@click.option("-n", "--name", help="Name of the TV to manage.")
@click.pass_context
def cli(ctx: click.Context, debug: bool = False, name: Optional[str] = None) -> None:
    """Command line webOS remote for LG TVs."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    config_path, full_config = read_config()
    name = name or full_config.get("_default")

    possible_tvs = list(full_config.keys())
    try:
        possible_tvs.remove("_default")
    except ValueError:
        pass

    if name and name not in possible_tvs:
        click.secho(
            f"No entry with the name '{name}' was found in the configuration at {config_path}. Names found: {', '.join(possible_tvs)}",
            fg="red",
            err=True,
        )
        sys.exit(1)

    tv_config = full_config.get(name, {})
    ctx.obj = {
        "config_path": config_path,
        "full_config": full_config,
        "tv_name": name,
        "tv_config": tv_config,
    }


if __name__ == "__main__":
    cli()
