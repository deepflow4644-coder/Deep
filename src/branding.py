"""
branding.py

Takes the raw generated background image and overlays:
- The Hindi fact text
- The "Itihas AI" branding tag

SETTINGS (change here if needed):
- FONT_PATH: path to a Devanagari-supporting font (must be added to assets/fonts/)
- FONT_SIZE / BRAND_FONT_SIZE: text sizes
- TEXT_COLOR / BRAND_COLOR: colors
- BRAND_TEXT: the branding string shown on every image
"""

import os
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "NotoSansDevanagari-Bold.ttf")
FONT_SIZE = 48
BRAND_FONT_SIZE = 28
TEXT_COLOR = (255, 255, 255)
BRAND_COLOR = (255, 215, 0)
BRAND_TEXT = "Itihas AI"


def add_branding(image_path, fact_text, output_path):
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    brand_font = ImageFont.truetype(FONT_PATH, BRAND_FONT_SIZE)

    width, height = image.size
    margin = 40
    max_width = width - (2 * margin)

    wrapped_lines = _wrap_text(fact_text, font, max_width, draw)
    text_block_height = len(wrapped_lines) * (FONT_SIZE + 10)
    y = height - text_block_height - 100

    for line in wrapped_lines:
        draw.text((margin, y), line, font=font, fill=TEXT_COLOR)
        y += FONT_SIZE + 10

    draw.text((margin, height - 60), BRAND_TEXT, font=brand_font, fill=BRAND_COLOR)

    image.save(output_path)
    return output_path


def _wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines
