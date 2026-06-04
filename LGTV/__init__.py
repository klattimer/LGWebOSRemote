from __future__ import print_function
from inspect import getfullargspec

import json
import os
import sys
from time import sleep
import logging
import argparse

PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
if PACKAGE_PATH not in sys.path:
    sys.path.append(PACKAGE_PATH)

from scan import LGTVScan
from remote import LGTVRemote
from auth import LGTVAuth
from cursor import LGTVCursor


config_paths = [
    "/etc/lgtv/config.json",
    os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "lgtv/config.json"),
    os.path.expanduser("~/.lgtv/config.json"),
    "/opt/venvs/lgtv/config/config.json"
]


def get_commands():
    text = 'commands\n'
    commands = LGTVRemote.getCommands()
    for c in commands:
        args = getfullargspec(LGTVRemote.__dict__[c])
        line = ' ' + c
        if len(args.args) > 2:
            a = ' <' + '> <'.join(args.args[1:-1]) + '>'
            line += a
        text += line + '\n'
    return text


def parseargs(command, argv):
    args = getfullargspec(LGTVRemote.__dict__[command])
    args = args.args[1:-1]

    if len(args) != len(argv):
        raise Exception("Argument lengths do not match")

    output = {}
    for (i, a) in enumerate(args):
        if argv[i].lower() == "true":
            argv[i] = True
        elif argv[i].lower() == "false":
            argv[i] = False
        try:
            if command != "setTVChannel":
                f = int(argv[i])
                argv[i] = f
        except:
            try:
                f = float(argv[i])
                argv[i] = f
            except:
                pass
        output[a] = argv[i]
    return output


def find_config() -> str:
    for f in config_paths:
        if os.path.isfile(f):
            return f
    # no config file exists yet
    for f in config_paths:
        d = os.path.dirname(f)
        if os.path.exists(d) and os.access(d, os.W_OK):
            return f
    # no config dir exists yet
    for f in config_paths:
        d = os.path.dirname(f)
        dd = os.path.dirname(d)
        if os.path.exists(dd) and os.access(dd, os.W_OK):
            return f
    print("Cannot find suitable config path to write, create one in {}".format(" or ".join(config_paths)))
    raise Exception("No config file")

def write_config(filename: str, config):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(config, f)

def main():
    parser = argparse.ArgumentParser(
        'lgtv',
        description = '''LGTV Controller\nAuthor: Karl Lattimer <karl@qdh.org.uk>''',
        epilog = get_commands(),
        formatter_class = argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--name', '-n', default=None)
    parser.add_argument('command')
    parser.add_argument('args', nargs='*')
    parser.add_argument('--ssl', action='store_true')
    parser.add_argument('--debug', '-d', action='store_true', help='enable debug output')
    parser.add_argument('--list', '-l', action='store_true', help='list tv\'s and exit')
    parser.add_argument('--json', '-j', action='store_true', help='output in json format')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    config = {}

    filename = find_config()
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            config = json.load(f)

    if args.list:
        for tv in config.keys():
            if tv == '_default':
                continue
            if args.json:
                print(json.dumps(config))
            else:
                print(f"{tv}: {config[tv]['hostname']} ({config[tv]['ip']}, {config[tv]['mac']})")
        if not args.json:
            if '_default' in config.keys():
                print(f"Default is: {config['_default']}")
            else:
                print("No default specified")
        return

    if args.command == "scan":
        results = LGTVScan()
        if len(results) > 0:
            if args.json:
                print(json.dumps({
                    "result": "ok",
                    "count": len(results),
                    "list": results
                }))
            else:
                for result in results:
                    print(f"{result['tv_name']}: {result['address']}")
            sys.exit(0)
        else:
            if args.json:
                print(json.dumps({
                    "result": "failed",
                    "count": len(results)
                }))
            else:
                print("No LG TV's found")
            sys.exit(1)

    elif args.command == "auth":
        if len(args.args) != 2:
            print('lgtv auth <host> <tv_name>')
            sys.exit(1)
        host, name = args.args
        ws = LGTVAuth(name, host, ssl=args.ssl)
        ws.connect()
        ws.run_forever()
        sleep(1)
        config[name] = ws.serialise()
        write_config(filename, config)
        print(f"Wrote config file {filename}")
        sys.exit(0)

    elif args.command == "setDefault":
        name = args.args[0]
        if filename is None:
            print("No config file found")
            sys.exit(1)
        if name == '_default':
            print("Error: default cannot be _default")
            return
            
        if name not in config:
            print("TV not found in config")
            sys.exit(1)
        config["_default"] = name
        write_config(filename, config)
        print(f"Wrote default to config file {filename}")

    # These commands require a TV name and config
    else:
        try:
            kwargs = parseargs(args.command, args.args)
        except Exception:
            if args.command not in {"sendButton"}:
                parser.print_help()
                sys.exit(1)

        if args.name:
            name = args.name
        elif "_default" in config:
            name = config["_default"]
        else:
            print("A TV name is required. Set one with -n/--name or the setDefault command.")
            sys.exit(1)

        if name not in config:
            print(f"No entry with the name '{name}' was found in the configuration at {filename}.")
            sys.exit(1)

        if args.command == "sendButton":
            cursor = LGTVCursor(name, **config[name], ssl=args.ssl)
            cursor.connect()
            cursor.execute(args.args)
            return

        max_retries = 3
        for attempt in range(max_retries):
            try:
                ws = LGTVRemote(name, **config[name], ssl=args.ssl)

                if args.command == "on":
                    # "on" is special, it doesn't use a websocket connection
                    ws.on()
                    return

                ws.connect()
                ws.execute(args.command, kwargs)
                ws.run_forever()
                break
            except ConnectionResetError:
                if attempt < max_retries - 1:
                    wait = 5
                    print(f"Retrying in {wait} seconds...")
                    sleep(wait)
                else:
                    print("Max retries reached.  Script failed")
                    raise    
            except KeyboardInterrupt:
                ws.close()

if __name__ == '__main__':
    main()


