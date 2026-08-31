# Development container

A VS Code dev container that builds both halves of Firestarter and can talk to a
board over USB without any host setup.

Open the repository in VS Code and choose **Reopen in Container**.

## What you get

Python 3.12 on Debian, with:

- **PlatformIO** for building and flashing the AVR firmware
- The `firestarter` CLI installed in editable mode from `firestarter_app/`, so
  the command reflects your working tree immediately
- `avrdude` and the AVR toolchain
- GitHub CLI, Node 22, `uv`

The `vscode` user is added to the `dialout` group and `/dev` is bind-mounted
with `--privileged`, so a board on `/dev/ttyACM*` or `/dev/ttyUSB*` is reachable
from inside the container.

## What happens on first start

`post-create.sh` runs once:

1. Generates `/workspaces/platformio.ini` from the firmware submodule's own
   `platformio.ini`, adding a `[platformio]` section that redirects every path
   into `firestarter/`. This is what lets the PlatformIO IDE extension find the
   project from the repository root rather than only from inside the submodule.
2. Installs the CLI with `pip install -e firestarter_app`.
3. Fetches the PlatformIO package dependencies for the firmware.

Re-run step 1 by hand after changing the firmware's `platformio.ini`:

```bash
python3 .devcontainer/gen-platformio-ini.py
```

## Persistent volumes

PlatformIO's package cache, the pip cache and `~/.config` are named volumes, so
a rebuild does not re-download the toolchain.

## Python version

The container runs **Python 3.12**. The host application's CI runs on **3.11**,
and the difference has masked real CI breakage before — a change can pass here
and fail on the floor. Before trusting a green test run for anything that
matters, repeat it on 3.11:

```bash
uv venv --python 3.11 /tmp/py311
/tmp/py311/bin/python -m pip install -e 'firestarter_app[test]'
/tmp/py311/bin/python -m pytest firestarter_app/tests -o addopts="" -q
```

`-o addopts=""` is needed because the project sets `addopts = -ra -q`; passing
`-q` again suppresses the pass/fail count line.

## Submodules

`firestarter/` and `firestarter_app/` are submodules. If either is empty:

```bash
git submodule update --init --recursive
```
