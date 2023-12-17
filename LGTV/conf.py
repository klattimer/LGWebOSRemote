import json
import sys
from pathlib import Path
from typing import Dict, Tuple

# TODO: Should this be replaced with click.get_app_dir()?
search_paths = [
    "/etc/lgtv/config.json",
    "~/.lgtv/config.json",
    "/opt/venvs/lgtv/config/config.json",
]


def read_config() -> Tuple[Path, Dict]:
    # Check for existing config files
    for path in map(Path, search_paths):
        path = path.expanduser()
        if path.exists():
            with path.open() as fp:
                return path, json.load(fp)

    # Attempt to find place to write new config file
    for path in map(Path, search_paths):
        path = path.expanduser()

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            return path, {}
        except (FileExistsError, PermissionError):
            pass

    print(
        "Cannot find suitable config path to write, create one in",
        " or ".join(search_paths),
    )
    sys.exit(1)


def write_config(path: Path, config: Dict) -> None:
    with path.open("w") as fp:
        json.dump(config, fp)
