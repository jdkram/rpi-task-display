#!/usr/bin/env bash
# human-contributors: []; ai-contributors: [Claude]; status: "#ai-written"
set -euo pipefail

sudo apt install -y python3-numpy python3-spidev python3-pip

python3 -m pip install -r "$(dirname "$0")/requirements.txt" --break-system-packages
