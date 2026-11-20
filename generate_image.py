#!/usr/bin/env python3
"""Draw entry.png (1024x1024) for make.fun news-image-20261120.

Reads stories.json beside this script and lays out a one-page newspaper
front page: serif masthead, subtitle, a large red date line, then seven
stories, each with a dark tag chip, a bold one-line headline and a
two-line summary. Before drawing anything, every story is measured with
the real fonts and the headline/summary sizes are stepped down until
the whole block fits between the date rule and the footer, so no two
text lines can ever overlap. If hero.png sits beside this script, a
cropped band of it is placed as a strip under the date rule, but only
when the stories still fit at the minimum font sizes; otherwise the
strip is dropped and the pure text layout is used. Headlines are never
cut with an ellipsis. Pillow + stdlib only; no network, no randomness,
so repeated runs are byte-identical.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
CANVAS = (1024, 1024)

PAPER = (250, 247, 238)
INK = (18, 18, 18)
BODY = (52, 50, 46)
RED = (168, 32, 26)
GREY = (90, 86, 78)
RULE = (150, 145, 132)
CHIP = (18, 18, 18)
CHIP_TEXT = (250, 247, 238)
NUMERAL = (36, 68, 120)

FONTS = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_BOLD = "DejaVuSans-Bold.ttf"

MARGIN = 46
SOURCES_LINE = ("Sources: BBC  ·  Reuters  ·  CNBC  ·  IMD  ·  Sensor Tower  ·  "
                "The Times")

HERO_PATH = os.path.join(BASE, "hero.png")
HERO_CROP = (0, 380, 2560, 620)   # middle band of the 2560x960 hero
STRIP_GAP = 8

MIN_HEAD, MIN_SUM = 19, 14


def load(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def flow_text(draw, text, font, width, limit):
    """Greedy word wrap, capped at `limit` lines with an ellipsis tail."""
    rows = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            rows.append(current)
            current = word
    if current:
        rows.append(current)
    if len(rows) > limit:
        rows = rows[:limit]
        while rows and draw.textlength(rows[-1] + " ...", font=font) > width:
            rows[-1] = rows[-1].rsplit(" ", 1)[0]
        rows[-1] = rows[-1] + " ..."
    return rows


def lay_out(draw, stories, head_font, sum_font, width):
    """Measure every story; return (per-story rows, total height)."""
    total = 0
    laid = []
    for story in stories:
        head_rows = flow_text(draw, story["headline"], head_font, width, 1)
        sum_rows = flow_text(draw, story["summary"], sum_font, width, 2)
        laid.append((head_rows, sum_rows))
        block = (24 + 4                       # tag chip + gap
                 + len(head_rows) * (head_font.size + 4)
                 + len(sum_rows) * (sum_font.size + 5)
                 + 6)                         # breathing room + divider
        total += block
    return laid, total


def head_truncated(laid):
    """True if any headline row was cut with an ellipsis."""
    return any(row.endswith(" ...")
               for head_rows, _ in laid for row in head_rows)


def fit(draw, stories, width, room):
    """Largest headline/summary sizes that fit `room` with no headline cut.

    Returns (head_size, sum_size, laid, needed, fits).
    """
    head_size, sum_size = 24, 17
    while True:
        head_font = load(SANS_BOLD, head_size)
        sum_font = load(SANS, sum_size)
        laid, needed = lay_out(draw, stories, head_font, sum_font, width)
        fits = needed <= room and not head_truncated(laid)
        if fits:
            return head_size, sum_size, laid, needed, True
        if head_size <= MIN_HEAD and sum_size <= MIN_SUM:
            return head_size, sum_size, laid, needed, False
        # Step down independently so neither size goes below its minimum.
        if head_size > MIN_HEAD:
            head_size -= 1
        if sum_size > MIN_SUM:
            sum_size -= 1


def main():
    with open(os.path.join(BASE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    page = Image.new("RGB", CANVAS, PAPER)
    draw = ImageDraw.Draw(page)

    masthead_font = load(SERIF_BOLD, 56)
    subtitle_font = load(SANS, 22)
    date_font = load(SANS_BOLD, 40)
    chip_font = load(SANS_BOLD, 16)
    numeral_font = load(SANS_BOLD, 22)
    footer_font = load(SANS, 15)

    left = MARGIN
    right = CANVAS[0] - MARGIN
    text_w = right - left

    # --- Masthead + date -------------------------------------------------
    y = 22
    draw.text((CANVAS[0] // 2, y), data["title"], font=masthead_font,
              fill=INK, anchor="ma")
    y += 68
    draw.text((CANVAS[0] // 2, y), data["subtitle"], font=subtitle_font,
              fill=GREY, anchor="ma")
    y += 36
    draw.line([(left, y), (right, y)], fill=INK, width=3)
    y += 10
    draw.text((CANVAS[0] // 2, y), data["date_label"], font=date_font,
              fill=RED, anchor="ma")
    y += 54
    draw.line([(left, y), (right, y)], fill=INK, width=3)
    y += 16

    plain_top = y
    footer_rule_y = CANVAS[1] - 70

    # --- Hero strip? Only if the stories still fit with it in place. ----
    strip = None
    strip_top = None
    if os.path.exists(HERO_PATH):
        hero = Image.open(HERO_PATH).convert("RGB")
        band = hero.crop(HERO_CROP)
        strip_w = text_w
        strip_h = round((HERO_CROP[3] - HERO_CROP[1]) * strip_w
                        / (HERO_CROP[2] - HERO_CROP[0]))
        strip = band.resize((strip_w, strip_h), Image.LANCZOS)
        strip_top = plain_top + STRIP_GAP
        stories_top = strip_top + strip_h + STRIP_GAP
        room = footer_rule_y - stories_top
        head_size, sum_size, laid, needed, fits = fit(
            draw, data["stories"], text_w, room)
        print("fit with hero strip: headline=%d summary=%d needed=%d "
              "room=%d fits=%s" % (head_size, sum_size, needed, room, fits),
              file=sys.stderr)
        if not fits:
            print("hero strip dropped: stories do not fit even at minimum "
                  "font sizes", file=sys.stderr)
            strip = None
    if strip is None:
        stories_top = plain_top
        room = footer_rule_y - stories_top
        head_size, sum_size, laid, needed, fits = fit(
            draw, data["stories"], text_w, room)
        print("fit: headline=%d summary=%d needed=%d room=%d"
              % (head_size, sum_size, needed, room), file=sys.stderr)
        if not fits:
            sys.exit("stories do not fit even at minimum font sizes")

    head_font = load(SANS_BOLD, head_size)
    sum_font = load(SANS, sum_size)

    if strip is not None:
        page.paste(strip, (left, strip_top))

    # --- Stories ----------------------------------------------------------
    y = stories_top
    for idx, story in enumerate(data["stories"]):
        head_rows, sum_rows = laid[idx]
        top = y

        chip_w = draw.textlength(story["tag"], font=chip_font) + 18
        draw.rounded_rectangle([left, top, left + chip_w, top + 24],
                               radius=4, fill=CHIP)
        draw.text((left + 9, top + 2), story["tag"], font=chip_font,
                  fill=CHIP_TEXT)
        draw.text((right, top + 1), str(story["n"]), font=numeral_font,
                  fill=NUMERAL, anchor="ra")

        cursor = top + 24 + 4
        for row in head_rows:
            draw.text((left, cursor), row, font=head_font, fill=INK)
            cursor += head_size + 4
        for row in sum_rows:
            draw.text((left, cursor), row, font=sum_font, fill=BODY)
            cursor += sum_size + 5

        y = cursor + 6
        if idx < len(data["stories"]) - 1:
            draw.line([(left, y - 3), (right, y - 3)], fill=RULE, width=1)

    # --- Footer -----------------------------------------------------------
    draw.line([(left, footer_rule_y), (right, footer_rule_y)],
              fill=INK, width=2)
    foot_rows = flow_text(draw, data["footer"], footer_font, text_w, 2)
    fy = footer_rule_y + 8
    for row in foot_rows:
        draw.text((CANVAS[0] // 2, fy), row, font=footer_font, fill=GREY,
                  anchor="ma")
        fy += 19
    draw.text((CANVAS[0] // 2, fy + 2), SOURCES_LINE, font=footer_font,
              fill=GREY, anchor="ma")

    out_path = os.path.join(BASE, "entry.png")
    page.save(out_path, "PNG", optimize=True)
    print("wrote %s (%d bytes)" % (out_path, os.path.getsize(out_path)))


if __name__ == "__main__":
    main()
