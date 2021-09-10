# -*- coding: utf-8 -*-
from __future__ import print_function
from inspect import getargspec
import json
import os
import sys
from time import sleep
import logging

from .scan import LGTVScan
from .remote import LGTVRemote
from .auth import LGTVAuth


search_config = [
    "/etc/lgtv/config.json",
    "~/.lgtv/config.json",
    "/opt/venvs/lgtv/config/config.json"
]


def usage(error=None):
    if error:
        print ("Error: " + error)
    print ("LGTV Controller")
    print ("Author: Karl Lattimer <karl@qdh.org.uk>")
    print ("Usage: lgtv <command> [parameter]\n")
    print ("Available Commands:")

    print ("  -i                    interactive mode")

    print ("  scan")
    print ("  auth <host> <tv_name>")

    commands = LGTVRemote.getCommands()
    for c in commands:
        args = getargspec(LGTVRemote.__dict__[c])
        if len(args.args) > 1:
            a = ' <' + '> <'.join(args.args[1:-1]) + '>'
            print ('  <tv_name> ' + c + a)
        else:
            print ('  <tv_name> ' + c)


def parseargs(command, argv):
    args = getargspec(LGTVRemote.__dict__[command])
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


def main():
    if len(sys.argv) < 2:
        usage("Too few arguments")
        sys.exit(1)
    logging.basicConfig(level=logging.DEBUG)

    command = None
    filename = None
    config = {}

    filename = find_config()
    if filename is not None:
        try:
            with open(filename) as f:
                config = json.loads(f.read())
        except:
            pass

    if sys.argv[1] == "scan":
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

    if sys.argv[1] == "-i":
        pass
    elif sys.argv[1] == "auth":
        if len(sys.argv) < 3:
            usage("Hostname or IP is required for auth")
            sys.exit(1)
        if len(sys.argv) < 4:
            usage("TV name is required for auth")
            sys.exit(1)
        name = sys.argv[3]
        host = sys.argv[2]
        ws = LGTVAuth(name, host)
        ws.connect()
        ws.run_forever()
        sleep(1)
        config[name] = ws.serialise()
        if filename is not None:
            with open(filename, 'w') as f:
                f.write(json.dumps(config))
            print ("Wrote config file: " + filename)

        sys.exit(0)
    elif len(sys.argv) >= 2 and sys.argv[2] == "on":
        name = sys.argv[1]
        ws = LGTVRemote(name, **config[name])
        ws.on()
        sleep(1)
        sys.exit(0)
    else:
        try:
            args = parseargs(sys.argv[2], sys.argv[3:])
            name = sys.argv[1]
            command = sys.argv[2]
        except Exception as e:
            usage(str(e))
            sys.exit(1)

    try:
        ws = LGTVRemote(name, **config[name])
        ws.connect()
        if command is not None:
            ws.execute(command, args)
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()

if __name__ == '__main__':
    main()
