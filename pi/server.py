#!/usr/bin/env python3
# human-contributors: Jonny Kram; ai-contributors: [Claude]; status: "#ai-input"
"""Flask server for the Inky pHAT (red/black/white).

Endpoints:
  GET  /calendar  — render the month calendar (jellyfish backdrop + date grid)
  POST /task      — render a short text task
  GET  /health    — liveness check
"""

from __future__ import annotations

import calendar
import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

COLOUR = "red"
HERE = Path(__file__).parent
RESOURCES = HERE / "resources"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    except OSError:
        return ImageFont.load_default()


def _display() -> InkyPHAT:
    d = InkyPHAT(COLOUR)
    d.set_border(d.BLACK)
    return d


def _create_mask(source: Image.Image, allowed: tuple) -> Image.Image:
    """Transparency mask for the sprite sheet compositing used in calendar rendering."""
    mask = Image.new("1", source.size)
    for x in range(source.width):
        for y in range(source.height):
            if source.getpixel((x, y)) in allowed:
                mask.putpixel((x, y), 255)
    return mask


def render_calendar() -> None:
    """Month view: jellyfish backdrop on the left, date grid on the right.

    Adapted from the official pimoroni calendar-phat.py example.
    Today's date cell is inverted (black bg, white text).
    Other-month dates appear in red. Current-month dates in white.
    """
    d = _display()

    text_sprite = Image.open(RESOURCES / "calendar.png")
    text_mask = _create_mask(text_sprite, (d.WHITE,))

    img = Image.open(RESOURCES / "empty-backdrop.png")
    draw = ImageDraw.Draw(img)

    cal = calendar.Calendar()
    now = datetime.datetime.now()
    dates = cal.monthdatescalendar(now.year, now.month)

    col_w, col_h = 20, 13
    cols = 7
    rows = len(dates) + 1
    cal_w = 1 + ((col_w + 1) * cols)
    cal_h = 1 + ((col_h + 1) * rows)
    cal_x = d.WIDTH - cal_w - 2
    cal_y = 2

    draw.rectangle(
        (cal_x, cal_y, cal_x + cal_w - 1, cal_y + cal_h - 1),
        fill=d.BLACK, outline=d.WHITE,
    )

    # Paste month name from sprite sheet
    months_x, months_y = 2, 20
    month_w, month_h = 23, 9
    month_col = (now.month - 1) % 3
    month_row = (now.month - 1) // 3
    crop = (
        months_x + month_col * month_w,
        months_y + month_row * month_h,
        months_x + month_col * month_w + month_w,
        months_y + month_row * month_h + month_h,
    )
    month_mask = text_mask.crop(crop)
    img.paste(d.WHITE, (28, cal_y + 4), month_mask)

    # Year digits
    _print_number(img, text_mask, d, (28, cal_y + 5 + col_h), now.year, d.WHITE)

    # Day-name headers
    for x in range(cols):
        o_x = cal_x + (col_w + 1) * x
        day_mask = text_mask.crop((2 + 16 * x, 0, 2 + 16 * x + 16, 9))
        img.paste(d.WHITE, (o_x + 4, cal_y + 2), day_mask)
        draw.line((o_x + col_w + 1, cal_y, o_x + col_w + 1, cal_h))

    # Row separators
    for y in range(rows):
        o_y = cal_y + col_h + 1 + (col_h + 1) * y
        draw.line((cal_x, o_y, cal_w + cal_x - 1, o_y))

    # Date cells
    for row, week in enumerate(dates):
        cell_y = cal_y + 1 + (col_h + 1) * (row + 1)
        for col, day in enumerate(week):
            cell_x = cal_x + 1 + (col_w + 1) * col
            if (day.day, day.month) == (now.day, now.month):
                draw.rectangle(
                    (cell_x, cell_y, cell_x + col_w - 1, cell_y + col_h - 1),
                    fill=d.WHITE,
                )
                _print_number(img, text_mask, d, (cell_x + 3, cell_y + 3), day.day, d.BLACK)
            else:
                colour = d.WHITE if day.month == now.month else d.RED
                _print_number(img, text_mask, d, (cell_x + 3, cell_y + 3), day.day, colour)

    d.set_image(img)
    d.show()


def _print_number(
    img: Image.Image,
    text_mask: Image.Image,
    d: InkyPHAT,
    position: tuple,
    number: int,
    colour: int,
) -> None:
    num_margin, num_w, num_h = 2, 6, 7
    s_y = 11
    x, y = position
    for digit in str(number):
        s_x = num_margin + int(digit) * (num_w + num_margin)
        sprite = text_mask.crop((s_x, s_y, s_x + num_w, s_y + num_h))
        img.paste(colour, (x, y), sprite)
        x += 8


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.getlength(candidate) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def render_task(text: str) -> None:
    """Centred text: first line in red, continuation in black."""
    d = InkyPHAT(COLOUR)
    d.set_border(d.WHITE)

    img = Image.new("P", (d.WIDTH, d.HEIGHT), d.WHITE)
    draw = ImageDraw.Draw(img)
    font = _font(20)

    max_width = d.WIDTH - 16
    lines = _wrap_text(text, font, max_width)
    _, _, _, line_h = font.getbbox("Ag")
    line_h += 6
    y = (d.HEIGHT - len(lines) * line_h) // 2

    for i, line in enumerate(lines):
        colour = d.RED if i == 0 else d.BLACK
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (d.WIDTH - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=font, fill=colour)
        y += line_h

    d.set_image(img)
    d.show()


@app.get("/calendar")
def show_calendar():
    render_calendar()
    return jsonify({"ok": True})


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


@app.get("/test")
def test_pattern():
    """Diagnostic grid: vertical bars every 10px with column labels.

    Use this to map physical dead zones to pixel coordinates.
    White background, black bars at 0/10/20.../210, black labels at 0/20/40...
    Labels use black not red -- red pigment bleeds too much for fine text.
    """
    d = _display()
    img = Image.new("P", (d.WIDTH, d.HEIGHT), d.WHITE)
    draw = ImageDraw.Draw(img)
    font = _font(8, bold=False)

    for x in range(0, d.WIDTH, 10):
        draw.line((x, 0, x, d.HEIGHT - 1), fill=d.BLACK)
        if x % 20 == 0:
            draw.text((x + 1, 1), str(x), font=font, fill=d.BLACK)

    # Horizontal midline for reference
    draw.line((0, d.HEIGHT // 2, d.WIDTH - 1, d.HEIGHT // 2), fill=d.BLACK)

    d.set_image(img)
    d.show()
    return jsonify({"ok": True, "width": d.WIDTH, "height": d.HEIGHT})


@app.get("/test/solid/<colour>")
def test_solid(colour: str):
    """Fill the display with a single colour: white, black, or red."""
    d = _display()
    colour_map = {"white": d.WHITE, "black": d.BLACK, "red": d.RED}
    if colour not in colour_map:
        return jsonify({"error": f"Unknown colour '{colour}'. Use: white, black, red"}), 400
    img = Image.new("P", (d.WIDTH, d.HEIGHT), colour_map[colour])
    d.set_image(img)
    d.show()
    return jsonify({"ok": True, "colour": colour})


@app.get("/test/sizes")
def test_sizes():
    """Render 'Ag 012' at increasing font sizes to find the minimum legible size.

    Sizes 10, 14, 18, 24, 32 stacked top to bottom. All black on white.
    Stop when a row is clearly unreadable -- that's your floor.
    """
    d = _display()
    img = Image.new("P", (d.WIDTH, d.HEIGHT), d.BLACK)
    draw = ImageDraw.Draw(img)

    sizes = [10, 14, 18, 24, 32]
    y = 2
    for size in sizes:
        font = _font(size, bold=True)
        label = f"{size}pt: Ag 012"
        _, _, _, h = font.getbbox("Ag")
        if y + h + 2 > d.HEIGHT:
            break
        draw.text((4, y), label, font=font, fill=d.WHITE)
        y += h + 4

    d.set_image(img)
    d.show()
    return jsonify({"ok": True})


@app.get("/date")
def show_date():
    """Today's date, large and centred. Day-of-week above, date below.

    Inverted (white text on black): white pigment migrates more reliably
    on this panel than black.
    """
    d = _display()
    img = Image.new("P", (d.WIDTH, d.HEIGHT), d.BLACK)
    draw = ImageDraw.Draw(img)

    now = datetime.datetime.now()
    day_str = now.strftime("%A")
    date_str = now.strftime("%-d %B %Y")

    day_font = _font(18, bold=False)
    date_font = _font(28, bold=True)

    _, _, _, day_h = day_font.getbbox(day_str)
    _, _, _, date_h = date_font.getbbox(date_str)
    gap = 6
    total_h = day_h + gap + date_h
    y = (d.HEIGHT - total_h) // 2

    day_w = day_font.getlength(day_str)
    draw.text(((d.WIDTH - day_w) // 2, y), day_str, font=day_font, fill=d.WHITE)

    date_w = date_font.getlength(date_str)
    draw.text(((d.WIDTH - date_w) // 2, y + day_h + gap), date_str, font=date_font, fill=d.WHITE)

    d.set_image(img)
    d.show()
    return jsonify({"ok": True, "day": day_str, "date": date_str})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
