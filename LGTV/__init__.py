# -*- coding: utf-8 -*-
from __future__ import print_function
from inspect import getfullargspec

import json
import os
import sys
from time import sleep
import logging
import argparse
from .scan import LGTVScan
from .remote import LGTVRemote
from .auth import LGTVAuth
from .cursor import LGTVCursor


search_config = [
    "/etc/lgtv/config.json",
    "~/.lgtv/config.json",
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


def find_config():
    w = None
    for f in search_config:
        f = os.path.expanduser(f)
        f = os.path.abspath(f)
        d = os.path.dirname(f)
        if os.path.exists(d):
            if os.access(d, os.W_OK):
                w = f
            if os.path.exists(f):
                if os.access(f, os.W_OK):
                    return f
        elif os.access(os.path.dirname(d), os.W_OK):
            os.makedirs(d)
            w = f
    if w is None:
        print ("Cannot find suitable config path to write, create one in %s" % ' or '.join(search_config))
        raise Exception("No config file")
    return w


def write_config(filename, config):
    with open(filename, 'w') as f:
        f.write(json.dumps(config))


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
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    config = {}

    filename = find_config()
    if filename is not None:
        try:
            with open(filename) as f:
                config = json.loads(f.read())
        except:
            pass

    if args.command == "scan":
        results = LGTVScan()
        if len(results) > 0:
            print (json.dumps({
                "result": "ok",
                "count": len(results),
                "list": results
            }))
            sys.exit(0)
        else:
            print (json.dumps({
                "result": "failed",
                "count": len(results)
            }))
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
        if filename is not None:
            write_config(filename, config)
            print ("Wrote config file: " + filename)
        sys.exit(0)

    elif args.command == "setDefault":
        name = args.args[0]
        if filename is None:
            print("No config file found")
            sys.exit(1)
        if name not in config:
            print("TV not found in config")
            sys.exit(1)
        config["_default"] = name
        write_config(filename, config)
        print ("Wrote default to config file: " + filename)

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

        try:
            ws = LGTVRemote(name, **config[name], ssl=args.ssl)

            if args.command == "on":
                # "on" is special, it doesn't use a websocket connection
                ws.on()
                return

            ws.connect()
            ws.execute(args.command, kwargs)
            ws.run_forever()
        except KeyboardInterrupt:
            ws.close()


if __name__ == '__main__':
    main()
