---
human-contributors: Jonny Kram
ai-contributors: [Claude]
---

# rpi-zero-display

Send a task string from the command line and display it on an Inky pHAT e-ink screen attached to a Raspberry Pi Zero.

## What it does

A small Flask server runs on the Pi and listens for task updates. A shell script on your dev machine sends the current task over HTTP, and the Pi renders it centred on the e-ink display. The display retains its image without power, so it sits passively beneath your monitor until you update it.

## Quick start

### Pi setup

Copy the `pi/` directory to your Pi, then:

```bash
cd ~/rpi-zero-display
uv sync
sudo cp rpi-display.service /etc/systemd/system/
sudo systemctl enable --now rpi-display
```

The server listens on port 5000. Check it is running:

```bash
curl http://localhost:5000/health
# {"ok": true}
```

### Client setup

On your dev machine, add the `client/` script to your PATH:

```bash
ln -s /path/to/rpi-zero-display/client/task ~/.local/bin/task
```

If `rpi.local` does not resolve on your network, add this to your shell config:

```bash
export RPI_HOST=192.168.x.x  # replace with your Pi's IP
```

## Usage

```bash
task "writing API docs"
task "debugging the auth flow"
task "deep work: no interruptions"
```

The display updates within a few seconds. Text wraps automatically to fit the screen.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `RPI_HOST` | `rpi.local` | Hostname or IP of the Pi |
| `RPI_PORT` | `5000` | Port the server listens on |

Set these in your shell config (`~/.bashrc`, `~/.zshrc`, etc.) to persist them.

## Project structure

```
rpi-zero-display/
├── pi/
│   ├── server.py             # Flask server + display rendering
│   ├── pyproject.toml        # Pi-side dependencies
│   └── rpi-display.service   # systemd unit file
└── client/
    └── task                  # shell script for sending tasks
```

## Development

The Pi server depends on `inky[rpi,fonts]`, which requires hardware GPIO libraries. To work on rendering logic without a Pi, mock out the `InkyPHAT` import or test with `inky`'s built-in simulator mode.

Install Pi-side dependencies:

```bash
cd pi
uv sync
```

The DejaVu Bold font (`fonts-dejavu-core` apt package) is used for rendering. The server falls back to PIL's built-in bitmap font if it is not installed, but the result is noticeably smaller and less readable.

## Licence

MIT
