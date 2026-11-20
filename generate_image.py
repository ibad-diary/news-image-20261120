#!/usr/bin/env python3
"""Render the one-page newspaper front page for 20 November 2026.

Reads ``stories.json`` next to this script (seven world-news stories,
each with a headline and a short summary) and draws a 1024x1024
newspaper page with Pillow: a white paper background, the date set
large in red, one block per story with a thin rule between stories,
and a small footer.

Usage:

    python3 generate_image.py --out /tmp/preview.png

The default output is ``entry.png`` next to this script; pass
``--out`` whenever you only want a test render.
"""

import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
MARGIN = 48
GUTTER = 28

INK = (18, 18, 18)
RED = (178, 34, 34)
GREY = (110, 110, 110)
RULE = (190, 190, 190)
PAPER = (255, 255, 255)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    """Load a TrueType font, falling back to Pillow's built-in font."""
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, face, max_width):
    """Split text into lines that fit max_width, word by word."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=face) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def fit_lines(draw, text, face, max_width, max_lines):
    """Wrap text and clip it to max_lines, adding an ellipsis if cut."""
    lines = wrap(draw, text, face, max_width)
    if len(lines) <= max_lines:
        return lines
    clipped = lines[:max_lines]
    while clipped and draw.textlength(clipped[-1] + " …", font=face) > max_width:
        clipped[-1] = clipped[-1].rsplit(" ", 1)[0]
    clipped[-1] = clipped[-1] + " …"
    return clipped


def draw_lines(draw, lines, face, x, y, fill, spacing):
    """Draw lines top to bottom, returning the y below the last line."""
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += face.size + spacing
    return y


def story_block(draw, story, x, y, width):
    """Draw one story (tag, headline, summary) and return the next y."""
    tag_face = font(SANS_BOLD, 13)
    head_face = font(SERIF_BOLD, 20)
    body_face = font(SANS, 14)

    tag = story.get("tag", "").upper()
    if tag:
        y = draw_lines(draw, [tag], tag_face, x, y, RED, 2)
        y += 2

    headline = fit_lines(draw, story["headline"], head_face, width, 3)
    y = draw_lines(draw, headline, head_face, x, y, INK, 2)
    y += 2

    summary = fit_lines(draw, story["summary"], body_face, width, 4)
    y = draw_lines(draw, summary, body_face, x, y, (60, 60, 60), 2)
    return y


def render(data):
    """Build the 1024x1024 front page and return the Pillow image."""
    image = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(image)

    title = data.get("title", "THE WORLD TODAY")
    subtitle = data.get("subtitle", "")
    date_label = data.get("date_label", "FRIDAY 20 NOVEMBER 2026")
    footer = data.get("footer", "")
    stories = data["stories"]

    # --- Masthead -----------------------------------------------------
    y = 36
    title_face = font(SERIF_BOLD, 64)
    title_w = draw.textlength(title, font=title_face)
    draw.text(((PAGE - title_w) / 2, y), title, font=title_face, fill=INK)
    y += 64 + 10

    date_face = font(SERIF_BOLD, 40)
    date_text = "20 November 2026"
    date_w = draw.textlength(date_text, font=date_face)
    draw.text(((PAGE - date_w) / 2, y), date_text, font=date_face, fill=RED)
    y += 40 + 8

    label_face = font(SANS_BOLD, 15)
    label_w = draw.textlength(date_label, font=label_face)
    draw.text(((PAGE - label_w) / 2, y), date_label, font=label_face, fill=GREY)
    y += 15 + 6

    if subtitle:
        sub_face = font(SERIF, 17)
        sub_w = draw.textlength(subtitle, font=sub_face)
        draw.text(((PAGE - sub_w) / 2, y), subtitle, font=sub_face, fill=(70, 70, 70))
        y += 17 + 12

    draw.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=INK, width=3)
    y += 6
    draw.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=INK, width=1)
    y += 18

    # --- Stories in two columns ---------------------------------------
    column_w = (PAGE - 2 * MARGIN - GUTTER) // 2
    left_x = MARGIN
    right_x = MARGIN + column_w + GUTTER
    top = y

    split = (len(stories) + 1) // 2  # 4 on the left, 3 on the right
    for column, group in enumerate((stories[:split], stories[split:])):
        x = left_x if column == 0 else right_x
        cy = top
        for index, story in enumerate(group):
            cy = story_block(draw, story, x, cy, column_w)
            if index < len(group) - 1:
                cy += 8
                draw.line([(x, cy), (x + column_w, cy)], fill=RULE, width=1)
                cy += 12
        if column == 0:
            left_bottom = cy

    y = max(left_bottom, cy) + 10

    # --- Footer -------------------------------------------------------
    draw.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=RULE, width=1)
    y += 10
    foot_face = font(SANS, 12)
    foot_lines = fit_lines(draw, footer, foot_face, PAGE - 2 * MARGIN, 2)
    draw_lines(draw, foot_lines, foot_face, MARGIN, y, GREY, 2)

    return image


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="Render the front page.")
    parser.add_argument(
        "--out",
        default=os.path.join(here, "entry.png"),
        help="output PNG path (default: entry.png next to this script)",
    )
    args = parser.parse_args()

    with open(os.path.join(here, "stories.json"), encoding="utf-8") as handle:
        data = json.load(handle)

    image = render(data)
    image.save(args.out, format="PNG")
    print("wrote %s (%dx%d)" % (args.out, image.width, image.height))


if __name__ == "__main__":
    main()
