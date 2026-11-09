---
human-contributors: Jonny Kram
ai-contributors: [Claude]
---

# rpi-zero-display

Send tasks or calendar events to an Inky pHAT (red/black/white) e-ink display on a Raspberry Pi Zero.

## What it does

A Flask server runs on the Pi and listens for display updates. Two client scripts on your dev machine push content over HTTP:

- `task "text"` -- renders text centred on the display, first line in red
- `cal` -- renders a month calendar grid on the display

The display retains its image without power.

## Pi setup

### 1. WiFi

**While the SD card is mounted on your dev machine**, edit the `wpa_supplicant.conf` directly:

```bash
sudo nano /media/jdkram/rootfs/etc/wpa_supplicant/wpa_supplicant.conf
```

Add your network inside the file:

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=GB

network={
    ssid="YourNetworkName"
    psk="YourPassword"
}
```

Replace `YourNetworkName` and `YourPassword`. Save, eject the SD card, and reinsert it in the Pi.

If you have multiple networks (home + work, etc.), add extra `network={ }` blocks.

### 2. SSH

Use Raspberry Pi Imager's "OS Customisation" (gear icon) to configure before flashing:

- Set username to `jdkram`
- Paste your public key (`~/.ssh/id_ed25519.pub`) into the SSH authorised keys field
- Enable SSH

Hostname is `pi0`, connect with:

```bash
ssh jdkram@pi0.local
```

If `pi0.local` does not resolve, find the Pi's IP from your router and use that, or set:

```bash
export RPI_HOST=192.168.x.x
```

### 3. Install the server

Copy the `pi/` directory to the Pi, then SSH in and run the install script:

```bash
ssh pi0_jdkram "mkdir -p ~/rpi-zero-display"
scp -r pi/ pi0_jdkram:~/rpi-zero-display/
ssh pi0_jdkram
bash ~/rpi-zero-display/pi/install.sh
sudo cp ~/rpi-zero-display/pi/rpi-display.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now rpi-display
```

Check it is running:

```bash
curl http://pi0.local:5000/health
# {"ok": true}
```

## Client setup

Add both client scripts to your PATH:

```bash
ln -s /path/to/rpi-zero-display/client/task ~/.local/bin/task
ln -s /path/to/rpi-zero-display/client/cal ~/.local/bin/cal
```

## Deployment

```bash
make deploy            # rsync pi/ to the Pi, then restart the service
make restart           # restart the service without transferring files
make logs              # tail journalctl output from the service
make ssh               # open a shell on the Pi
```

Override the host if `pi0.local` doesn't resolve:

```bash
make deploy HOST=192.168.1.42
```

### Diagnostic commands

```bash
make test-grid         # render a column grid (every 10px, labelled at 20px intervals)
make test-solid-black  # fill display black — shows up dead zones
make test-solid-red    # fill display red
make test-solid-white  # full white flush
```

## Usage

```bash
# Display a task
task "writing API docs"
task "deep work: no interruptions"

# Display this month's calendar grid
cal
```

### Display layout

**Task mode:** text centred, first line in red, continuation in black.

**Calendar mode:** jellyfish backdrop on the left, month grid on the right. Today's date is highlighted; other-month dates appear in red.

## Configuration

| Variable   | Default    | Description                    |
|------------|------------|--------------------------------|
| `RPI_HOST` | `pi0.local`| Hostname or IP of the Pi       |
| `RPI_PORT` | `5000`     | Port the server listens on     |

Set in your shell config to persist them.

## Project structure

```
rpi-zero-display/
├── pi/
│   ├── server.py             # Flask server + display rendering
│   ├── requirements.txt      # Pi-side dependencies
│   ├── install.sh            # dependency install script
│   ├── resources/            # sprite sheets for calendar rendering
│   └── rpi-display.service   # systemd unit file
└── client/
    ├── task                  # send a task string
    └── cal                   # send today's calendar events
```

## Development notes

The Pi server depends on `inky` which requires SPI and GPIO. To work on rendering without a Pi, mock out `InkyPHAT` or use Inky's built-in simulator mode.

The display is the red/black/white Inky pHAT variant (212×104 px). Changing `InkyPHAT("red")` to `InkyPHAT("black")` or `InkyPHAT("yellow")` adapts it to other variants -- the layout logic is the same.

## Licence

MIT
