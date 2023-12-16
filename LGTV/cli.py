import json
import logging
import sys
from time import sleep
from typing import Dict, Optional, Tuple

import click

from LGTV.auth import LGTVAuth
from LGTV.conf import read_config, write_config
from LGTV.cursor import LGTVCursor
from LGTV.remote import LGTVRemote
from LGTV.scan import LGTVScan


@click.group
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


@cli.command
def scan() -> None:
    """Scan the local network for LG TVs."""
    results = LGTVScan()

    if len(results) > 0:
        click.echo(json.dumps({"result": "ok", "count": len(results), "list": results}))
        sys.exit(0)
    else:
        click.echo(json.dumps({"result": "failed", "count": len(results)}))
        sys.exit(1)


@cli.command
@click.argument("host")
@click.argument("name")
@click.option("-s", "--ssl", is_flag=True, help="Connect to TV using SSL.")
@click.pass_obj
def auth(obj: Dict, host: str, name: str, ssl: bool = False) -> None:
    """Connect to a new TV."""
    if name.startswith("_"):
        click.secho(
            "TV names are not allowed to start with an underscore", fg="red", err=True
        )
        sys.exit(1)

    ws = LGTVAuth(name, host, ssl=ssl)
    ws.connect()
    ws.run_forever()
    sleep(1)
    config = obj["full_config"]
    config[name] = ws.serialise()
    write_config(obj["config_path"], config)
    click.echo(f"Wrote config file: {obj['config_path']}")


@cli.command
@click.argument("name")
@click.pass_obj
def set_default(obj: Dict, name: str) -> None:
    """Change the default TV to interact with."""
    config = obj["full_config"]
    if name == "_default" or name not in config:
        click.secho("TV not found in config", fg="red", err=True)
        sys.exit(1)

    config["_default"] = name
    write_config(obj["config_path"], config)
    click.echo(f"Default TV set to '{name}'")


@cli.command
@click.argument("buttons", nargs=-1)
@click.option("-s", "--ssl", is_flag=True, help="Connect to TV using SSL.")
@click.pass_obj
def send_button(obj: Dict, buttons: Tuple[str], ssl: bool = False) -> None:
    """Sends button presses from the remote."""
    cursor = LGTVCursor(obj["tv_name"], **obj["tv_config"], ssl=ssl)
    cursor.connect()
    cursor.execute(buttons)


@cli.command
@click.pass_obj
def on(obj: Dict) -> None:
    """Turn on TV using Wake-on-LAN."""
    remote = LGTVRemote(obj["tv_name"], **obj["tv_config"])
    remote.on()


if __name__ == "__main__":
    cli()
