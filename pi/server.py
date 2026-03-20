#!/usr/bin/env python3
# human-contributors: Jonny Kram; ai-contributors: [Claude]; status: "#ai-written"
"""Flask server that renders task text on an Inky pHAT e-ink display."""

import textwrap

from flask import Flask, jsonify, request
from inky.auto import InkyPHAT
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 18
LINE_HEIGHT = 24
PADDING = 8


def _load_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except OSError:
        return ImageFont.load_default()


def render_task(text: str) -> None:
    """Render text centred on the Inky pHAT display."""
    display = InkyPHAT("black")
    display.set_border(display.WHITE)

    img = Image.new("P", (display.WIDTH, display.HEIGHT), display.WHITE)
    draw = ImageDraw.Draw(img)
    font = _load_font()

    # Wrap to fit display width with padding
    usable_width = display.WIDTH - (PADDING * 2)
    # Rough chars-per-line based on average glyph width at this font size
    chars_per_line = usable_width // (FONT_SIZE // 2)
    lines = textwrap.wrap(text, width=chars_per_line) or [""]

    total_height = len(lines) * LINE_HEIGHT
    y = (display.HEIGHT - total_height) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (display.WIDTH - text_width) // 2
        draw.text((x, y), line, font=font, fill=display.BLACK)
        y += LINE_HEIGHT

    display.set_image(img)
    display.show()


@app.post("/task")
def set_task():
    data = request.get_json(silent=True)
    if not data or "task" not in data:
        return jsonify({"error": "Missing 'task' field"}), 400

    task = str(data["task"]).strip()
    if not task:
        return jsonify({"error": "Task cannot be empty"}), 400

    render_task(task)
    return jsonify({"ok": True, "task": task})


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
