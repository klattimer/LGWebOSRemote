How-to: Install LGWebOSRemote on LibreELEC
==========================================

This guide explains how to install the LGWebOSRemote CLI utility on limited platforms where
things like Python, PIP and SSDP may not be available or possible to install, but where
Docker is an option. The guide applies to LibreELEC specifically (which is exactly such a
limited platform) but should work just as fine for any other platform that fits the criteria.

Pre-requisites
--------------------

* Obviously, install the Docker Kodi add-on.
* Make sure your LibreELEC system has network connectivity.
* Find out how to use SSH to connect to the LibreELEC system.
* Connect via SSH, create a directory to hold the Dockerfile, then continue below.

Dockerfile
---------------

```dockerfile
FROM python:3.12

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN . /opt/venv/bin/activate && pip install git+https://github.com/klattimer/LGWebOSRemote
RUN mkdir -m 777 -p /opt/venvs/lgtv/config
RUN echo '{"mytv" : {"ip": "10.0.0.69", "client-key": "", "mac-address": "34:e6:e6:a5:c8:3c"}}' > /opt/venvs/lgtv/config/config.json
RUN useradd app
RUN chown app:app /opt/venvs/lgtv/config
RUN chown app:app /opt/venvs/lgtv/config/config.json

USER app

RUN . /opt/venv/bin/activate && exec lgtv auth --ssl 10.0.0.69 mytv
RUN . /opt/venv/bin/activate && exec lgtv setDefault mytv

CMD . /opt/venv/bin/activate && exec lgtv
```

You'll need to adapt the Dockerfile slightly to fit your system:

* Change the `ip` and `mac-address` settings in the JSON array that is written to `config.json`.
* Change the IP and TV name in the `auth` command.
* If you changed the TV name, also change it in the `setDefault` command right below.

Building it
---------------

```bash
docker build --network=host -t lgtv/remote .
```

* The `--network=host` part is vital!
* While building, your TV will prompt you to authenticate an app. Be ready to accept that dialog.
* Once built, the Docker image contains configuration to operate one TV.

Running it
---------------

```bash
# example with screenOn command
docker run -t --rm lgtv/remote lgtv --ssl screenOn
```

* The `--rm` is added to avoid leaving one dead container for every execution.
* The `-t` is optional but nice for continuous feedback.

The workarounds
-------------------------

1. LibreELEC won't allow network scan with SSDP to discover the TV, so you can't use `lgtv scan` - you have to use the IP manually.
2. Docker (or at least the base image used here) won't allow the configuration file to be automatically created - the build routine must create it.
3. Docker won't persist the configuration file changes so you can't store the client key - the `auth` step is done when building to make sure the built image contains the right configuration.
4. The base image has no home directory so the configuration file has to be written to `/opt/venvs/lgtv/config/config.json`.
