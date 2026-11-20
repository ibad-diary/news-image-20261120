#!/usr/bin/env python3
"""Round-2 front page for news-image-20261120: 37 stories, one image.

Reads the stories.json sitting next to this file and paints a dense
1024x1024 newspaper front page with Pillow: top line, serif masthead
with a red date badge, a four-story kicker, region chips, a numbers
strip, three big illustrated leads, ten small illustrated features,
and a two-column roll of 24 one-line briefs, closed by a date-check
footer. All artwork is vector shapes drawn in code; nothing is
downloaded and nothing is random, so the output is deterministic.
The page is laid out top to bottom with running y positions, and the
script refuses to finish if the footer would run past the bottom
edge, instead of silently clipping text.

Run:  python3 generate_image.py   (writes entry.png next to itself)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SIDE = 1024
PAD = 26
INNER = SIDE - 2 * PAD

PAPER = (250, 247, 238)
CARD = (255, 253, 246)
INK = (20, 20, 20)
BODY = (58, 56, 50)
MUTED = (96, 92, 84)
RED = (172, 34, 26)
DEEPRED = (122, 20, 16)
NAVY = (31, 58, 96)
GOLD = (176, 124, 24)
TEAL = (14, 110, 110)
GREEN = (34, 122, 60)
RUST = (122, 74, 30)
VIOLET = (96, 52, 130)
LINE = (178, 172, 156)

DEJAVU = "/usr/share/fonts/truetype/dejavu"
LIBERATION = "/usr/share/fonts/truetype/liberation"
SERIF_B = os.path.join(DEJAVU, "DejaVuSerif-Bold.ttf")
SERIF_I = os.path.join(LIBERATION, "LiberationSerif-Italic.ttf")
SANS = os.path.join(DEJAVU, "DejaVuSans.ttf")
SANS_B = os.path.join(DEJAVU, "DejaVuSans-Bold.ttf")

ORDER = ["Europe", "Mideast", "Asia", "Africa", "Americas", "Oceania",
         "World"]
PAINT = {"Europe": NAVY, "Mideast": TEAL, "Asia": GOLD, "Africa": RUST,
         "Americas": VIOLET, "Oceania": TEAL, "World": (90, 88, 80)}


def typeface(path, size):
    return ImageFont.truetype(path, size)


def fit_text(draw, text, font, width, limit):
    """Word-wrap `text` to `width`, at most `limit` lines, ellipsis tail."""
    out, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            out.append(current)
            current = word
    if current:
        out.append(current)
    if len(out) > limit:
        out = out[:limit]
        while out and draw.textlength(out[-1] + " ...", font=font) > width:
            out[-1] = out[-1].rsplit(" ", 1)[0]
        out[-1] = out[-1] + " ..."
    return out


# --- pictures -----------------------------------------------------------

def picture_cyclone(draw, x, y, w, h):
    """Cyclone over the Bay of Bengal: sea, coast, spiral, landfall pin."""
    draw.rectangle([x, y, x + w, y + h], fill=(24, 68, 96))
    draw.polygon([(x, y + h), (x + w // 2, y + h // 3), (x + w, y + h)],
                 fill=(196, 164, 110))
    cx, cy = x + w // 3, y + h // 2
    for r in (30, 22, 14):
        draw.arc([cx - r, cy - r, cx + r, cy + r], 30, 320,
                 fill=(255, 255, 255), width=4)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
    draw.ellipse([x + w - 34, y + h - 30, x + w - 18, y + h - 14],
                 fill=RED)
    f = typeface(SANS_B, 10)
    draw.text((x + 8, y + h - 18), "LANDFALL · GUSTS 110 KM/H", font=f,
              fill=(255, 255, 255))


def picture_rockets(draw, x, y, w, h):
    """Night sky over Kyiv: skyline and missile trails."""
    draw.rectangle([x, y, x + w, y + h], fill=(16, 22, 44))
    for i, bh in enumerate([40, 58, 34, 66, 46]):
        bx = x + 10 + i * ((w - 20) // 5)
        draw.rectangle([bx, y + h - 30 - bh, bx + (w - 20) // 5 - 6,
                        y + h - 30], fill=(8, 12, 28))
    draw.rectangle([x, y + h - 30, x + w, y + h], fill=(8, 12, 28))
    for i, (sx, sy) in enumerate([(20, 26), (70, 14), (120, 30), (170, 18)]):
        draw.line([x + sx, y + sy, x + sx + 46, y + sy + 26],
                  fill=(255, 120, 60), width=3)
        draw.ellipse([x + sx + 44, y + sy + 24, x + sx + 50, y + sy + 30],
                     fill=(255, 200, 90))
    f = typeface(SANS_B, 10)
    draw.text((x + 8, y + 6), "01:25 LOCAL · 7 WAVES", font=f,
              fill=(255, 200, 90))


def picture_cop(draw, x, y, w, h):
    """COP31: globe, thermometer, red FINAL DAY badge."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 64, 78))
    cx, cy = x + w // 3, y + h // 2
    draw.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], outline=(255, 255, 255),
                 width=3)
    draw.line([cx - 34, cy, cx + 34, cy], fill=(255, 255, 255), width=2)
    draw.arc([cx - 16, cy - 34, cx + 16, cy + 34], 90, 270,
             fill=(255, 255, 255), width=2)
    tx = x + 2 * w // 3
    draw.rounded_rectangle([tx, y + 12, tx + 14, y + h - 22], radius=7,
                           outline=(255, 255, 255), width=2)
    draw.rectangle([tx + 3, y + h - 34, tx + 11, y + h - 24], fill=RED)
    draw.ellipse([tx - 3, y + h - 26, tx + 17, y + h - 6], fill=RED)
    draw.rounded_rectangle([x + w - 118, y + 8, x + w - 8, y + 38], radius=4,
                           fill=RED)
    f = typeface(SANS_B, 12)
    draw.text((x + w - 63, y + 15), "FINAL DAY", font=f,
              fill=(255, 255, 255), anchor="ma")


def picture_sunset(draw, x, y, w, h):
    """GTA VI launch sunset with skyline and a big $2.36bn tag."""
    bands = [(232, 120, 40), (214, 84, 96), (128, 72, 140), (64, 48, 110)]
    step = h // 4
    for i, colour in enumerate(bands):
        draw.rectangle([x, y + i * step, x + w, y + (i + 1) * step],
                       fill=colour)
    draw.ellipse([x + w // 2 - 24, y + 10, x + w // 2 + 24, y + 58],
                 fill=(252, 214, 110))
    base = y + h - 24
    for i, bh in enumerate([30, 48, 26, 56, 36, 44]):
        bx = x + 8 + i * ((w - 16) // 6)
        draw.rectangle([bx, base - bh, bx + (w - 16) // 6 - 4, base],
                       fill=(24, 18, 44))
    draw.rectangle([x, base, x + w, y + h], fill=(24, 18, 44))
    f = typeface(SANS_B, 15)
    draw.text((x + 8, y + 6), "$2.36bn", font=f, fill=(255, 255, 255))


def mini(draw, kind, x, y, w, h, colour):
    """A small coloured banner with one white glyph for a feature card."""
    draw.rectangle([x, y, x + w, y + h], fill=colour)
    cx, cy = x + w // 2, y + h // 2
    white = (255, 255, 255)
    if kind == "chartdown":
        draw.line([(x + 10, y + 10), (x + w // 3, y + h - 18),
                   (x + 2 * w // 3, y + h // 2), (x + w - 10, y + h - 10)],
                  fill=white, width=3)
        draw.polygon([(x + w - 16, y + h - 16), (x + w - 8, y + h - 10),
                      (x + w - 16, y + h - 4)], fill=white)
    elif kind == "planet":
        draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=white)
        draw.ellipse([cx - 22, cy - 4, cx + 22, cy + 4], outline=white,
                     width=2)
    elif kind == "flags":
        for i, off in enumerate((0, 26, 52)):
            draw.line([x + 16 + off, y + 8, x + 16 + off, y + h - 8],
                      fill=white, width=2)
            draw.rectangle([x + 16 + off, y + 8, x + 34 + off, y + 18],
                           fill=white)
    elif kind == "bars":
        for i, bh in enumerate([12, 20, 28]):
            bx = x + 16 + i * 18
            draw.rectangle([bx, y + h - 8 - bh, bx + 12, y + h - 8],
                           fill=white)
    elif kind == "sunset":
        picture_sunset(draw, x, y, w, h)
    elif kind == "bat":
        draw.line([x + 14, y + h - 10, x + w - 30, y + 10], fill=white,
                  width=5)
        draw.ellipse([x + w - 34, y + 6, x + w - 12, y + 28], fill=white)
    elif kind == "vote":
        f = typeface(SANS_B, 13)
        draw.text((cx, cy - 16), "THIRD", font=f, fill=white, anchor="ma")
        draw.text((cx, cy + 2), "TERM", font=f, fill=white, anchor="ma")
    elif kind == "waves":
        for j, yy in enumerate((y + 12, y + 22, y + 32)):
            draw.arc([x + 10 + j * 6, yy, x + w - 10 - j * 6, yy + 16], 180,
                     360, fill=white, width=2)
    elif kind == "rally":
        for i, off in enumerate((-22, 0, 22)):
            draw.ellipse([cx + off - 8, y + 8, cx + off + 8, y + 24],
                         fill=white)
            draw.pieslice([cx + off - 14, y + 22, cx + off + 14, y + 44],
                          180, 360, fill=white)
    elif kind == "pill":
        draw.rounded_rectangle([x + 14, cy - 9, x + w - 14, cy + 9], radius=9,
                               fill=white)
        draw.line([cx, cy - 9, cx, cy + 9], fill=colour, width=2)


LEAD_ART = {"cyclone": picture_cyclone, "rockets": picture_rockets,
            "cop": picture_cop}


def build(data):
    img = Image.new("RGB", (SIDE, SIDE), PAPER)
    draw = ImageDraw.Draw(img)
    total = len(data["leads"]) + len(data["features"]) + len(data["briefs"])
    assert total == 37, "expected 37 stories, got %d" % total
    counts = {name: 0 for name in ORDER}
    for story in data["leads"] + data["features"] + data["briefs"]:
        counts[story["region"]] += 1

    lead_h, feat_h, brief_step = 96, 42, 13
    y = 12

    # top line
    f_top = typeface(SANS_B, 10)
    draw.text((PAD, y), data["topline_left"], font=f_top, fill=INK)
    draw.text((SIDE - PAD, y), data["topline_right"], font=f_top, fill=INK,
              anchor="ra")
    y += 15
    draw.line([(PAD, y), (SIDE - PAD, y)], fill=INK, width=2)
    y += 6

    # masthead, shrunk until it clears the badge at the right
    size = 46
    while True:
        f_head = typeface(SERIF_B, size)
        if draw.textlength(data["masthead"], font=f_head) <= 2 * (
                SIDE - PAD - 78 - 8 - SIDE // 2):
            break
        size -= 1
    draw.text((SIDE // 2, y), data["masthead"], font=f_head, fill=INK,
              anchor="ma")
    draw.rounded_rectangle([SIDE - PAD - 78, y + 4, SIDE - PAD, y + 46],
                           radius=4, fill=RED)
    f_badge = typeface(SANS_B, 12)
    draw.text((SIDE - PAD - 39, y + 9), "FRIDAY", font=f_badge,
              fill=(255, 255, 255), anchor="ma")
    draw.text((SIDE - PAD - 39, y + 26), "20 NOV 2026", font=f_badge,
              fill=(255, 255, 255), anchor="ma")
    y += 56
    draw.text((SIDE // 2, y), data["kicker"], font=typeface(SERIF_I, 15),
              fill=DEEPRED, anchor="ma")
    y += 22
    draw.line([(PAD, y), (SIDE - PAD, y)], fill=INK, width=2)
    y += 6

    # region chips
    f_chip = typeface(SANS_B, 12)
    x = PAD
    for name in ORDER:
        label = "%s %d" % (name.upper(), counts[name])
        cw = draw.textlength(label, font=f_chip) + 18
        draw.rounded_rectangle([x, y, x + cw, y + 24], radius=3,
                               fill=PAINT[name])
        draw.text((x + 9, y + 4), label, font=f_chip, fill=(255, 255, 255))
        x += cw + 6
    y += 30

    # numbers strip
    f_big = typeface(SERIF_B, 27)
    f_cap = typeface(SANS, 10)
    cell = INNER // 6
    top = y
    for i, num in enumerate(data["numbers"]):
        cx = PAD + i * cell + cell // 2
        draw.text((cx, top), num["big"], font=f_big, fill=RED, anchor="ma")
        cy = top + 32
        for row in fit_text(draw, num["cap"], f_cap, cell - 12, 3):
            draw.text((cx, cy), row, font=f_cap, fill=BODY, anchor="ma")
            cy += 12
        if i:
            draw.line([(PAD + i * cell, top + 2),
                       (PAD + i * cell, top + 70)], fill=LINE, width=1)
    y = top + 74
    draw.line([(PAD, y), (SIDE - PAD, y)], fill=LINE, width=1)
    y += 8

    # lead cards
    f_lk = typeface(SANS_B, 10)
    f_lh = typeface(SANS_B, 18)
    f_ls = typeface(SANS, 12)
    gap = 10
    cw = (INNER - 2 * gap) // 3
    lead_top = y
    for i, story in enumerate(data["leads"]):
        x0 = PAD + i * (cw + gap)
        draw.rectangle([x0, y, x0 + cw, y + lead_h + 138], outline=LINE,
                       width=1, fill=CARD)
        LEAD_ART[story["art"]](draw, x0 + 1, y + 1, cw - 2, lead_h)
        cy = y + lead_h + 8
        draw.text((x0 + 10, cy), story["place"], font=f_lk,
                  fill=PAINT[story["region"]])
        draw.text((x0 + cw - 10, cy), str(story["n"]), font=f_lk, fill=RED,
                  anchor="ra")
        cy += 14
        for row in fit_text(draw, story["headline"], f_lh, cw - 20, 3):
            draw.text((x0 + 10, cy), row, font=f_lh, fill=INK)
            cy += 22
        for row in fit_text(draw, story["summary"], f_ls, cw - 20, 3):
            draw.text((x0 + 10, cy), row, font=f_ls, fill=BODY)
            cy += 16
    y = lead_top + lead_h + 138 + 8

    # feature cards, 5 across x 2 rows
    f_fk = typeface(SANS_B, 9)
    f_fh = typeface(SANS_B, 13)
    f_fs = typeface(SANS, 10)
    fgap = 8
    fw = (INNER - 4 * fgap) // 5
    row_h = feat_h + 98
    for r in range(2):
        for c in range(5):
            story = data["features"][r * 5 + c]
            x0 = PAD + c * (fw + fgap)
            y0 = y + r * (row_h + fgap)
            draw.rectangle([x0, y0, x0 + fw, y0 + row_h], outline=LINE,
                           width=1, fill=CARD)
            mini(draw, story["art"], x0 + 1, y0 + 1, fw - 2, feat_h,
                 PAINT[story["region"]])
            cy = y0 + feat_h + 6
            draw.text((x0 + 8, cy), story["place"], font=f_fk,
                      fill=PAINT[story["region"]])
            draw.text((x0 + fw - 8, cy), str(story["n"]), font=f_fk, fill=RED,
                      anchor="ra")
            cy += 13
            for row in fit_text(draw, story["headline"], f_fh, fw - 16, 3):
                draw.text((x0 + 8, cy), row, font=f_fh, fill=INK)
                cy += 16
            for row in fit_text(draw, story["summary"], f_fs, fw - 16, 2):
                draw.text((x0 + 8, cy), row, font=f_fs, fill=BODY)
                cy += 13
    y += 2 * row_h + fgap + 8

    # briefs, two columns
    f_bh = typeface(SANS_B, 12)
    draw.text((PAD, y), "ALSO ON FRIDAY 20 NOVEMBER — 24 MORE STORIES",
              font=f_bh, fill=INK)
    draw.text((SIDE - PAD, y), "place · what happened · source", font=f_bh,
              fill=MUTED, anchor="ra")
    y += 20
    draw.line([(PAD, y), (SIDE - PAD, y)], fill=INK, width=2)
    y += 4
    f_b = typeface(SANS, 11)
    f_bb = typeface(SANS_B, 11)
    col_w = (INNER - 24) // 2
    half = (len(data["briefs"]) + 1) // 2
    ends = []
    for col, group in enumerate((data["briefs"][:half],
                                 data["briefs"][half:])):
        x0 = PAD + col * (col_w + 24)
        cy = y
        for b in group:
            draw.text((x0, cy), "■ ", font=f_b, fill=RED)
            bx = x0 + 12
            head = b["place"] + " — "
            draw.text((bx, cy), head, font=f_bb, fill=INK)
            off = draw.textlength(head, font=f_bb)
            rows = fit_text(draw, b["text"] + "  (" + b["source"] + ")",
                            f_b, col_w - 12 - off, 2)
            ry = cy
            for j, row in enumerate(rows):
                if j == 0:
                    draw.text((bx + off, ry), row, font=f_b, fill=BODY)
                else:
                    draw.text((bx, ry), row, font=f_b, fill=BODY)
                ry += brief_step
            cy += max(brief_step, len(rows) * brief_step)
        ends.append(cy)
    y = max(ends) + 6

    # footer
    draw.line([(PAD, y), (SIDE - PAD, y)], fill=INK, width=2)
    y += 6
    f_foot = typeface(SANS, 9)
    for row in fit_text(draw, data["date_check"], f_foot, INNER, 2):
        draw.text((PAD, y), row, font=f_foot, fill=BODY)
        y += 12
    for row in fit_text(draw, data["sources"], f_foot, INNER, 2):
        draw.text((PAD, y + 2), row, font=f_foot, fill=MUTED)
        y += 12
    if y > SIDE - 4:
        sys.exit("footer overflows the page bottom (y=%d)" % y)
    return img


def main():
    with open(os.path.join(ROOT, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = build(data)
    out = os.path.join(ROOT, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote %s (%dx%d, %d bytes)"
          % (out, img.width, img.height, os.path.getsize(out)))


if __name__ == "__main__":
    main()
