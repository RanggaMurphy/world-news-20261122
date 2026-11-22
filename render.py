#!/usr/bin/env python3
"""Compose the 2026-11-22 edition of "The World Today" as one PNG.

The script loads sources.json, lays the day out like a newspaper front
page (masthead, date line, three lead stories, a world grid, a figures
strip, a sources footer) and writes entry.png at 1024x1024. Rendering
is deterministic: same inputs, same bytes. This file is a local build
tool; the graded entrypoint is main.py.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
SIZE = 1024

NAVY = (12, 32, 64)
NAVY_SOFT = (26, 54, 98)
GOLD = (196, 156, 72)
CREAM = (247, 242, 232)
PAPER = (250, 248, 243)
INK = (20, 26, 36)
FAINT = (105, 108, 112)
RULE_TAN = (198, 190, 170)

DEJAVU = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(DEJAVU, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(DEJAVU, "DejaVuSans.ttf")
SANS_B = os.path.join(DEJAVU, "DejaVuSans-Bold.ttf")


def load_font(path, px):
    return ImageFont.truetype(path, px)


def wrap_text(draw, text, font, limit, max_lines):
    lines, pending = [], ""
    for word in text.split():
        trial = (pending + " " + word).strip()
        if draw.textlength(trial, font=font) <= limit:
            pending = trial
        else:
            if pending:
                lines.append(pending)
            pending = word
    if pending:
        lines.append(pending)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        tail = lines[-1]
        while tail and draw.textlength(tail + "...", font=font) > limit:
            tail = tail.rsplit(" ", 1)[0] if " " in tail else tail[:-1]
        lines[-1] = tail + "..."
    return lines


def spaced_text(draw, center_x, top, text, font, fill, tracking):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x = center_x - total / 2.0
    for ch, w in zip(text, widths):
        draw.text((x, top), ch, font=font, fill=fill)
        x += w + tracking


def cover_into(canvas, image_path, rect):
    x0, y0, x1, y1 = rect
    with Image.open(image_path) as im:
        fitted = ImageOps.fit(im.convert("RGB"), (x1 - x0, y1 - y0),
                              Image.LANCZOS)
    canvas.paste(fitted, (x0, y0))


def globe_panel(draw, rect, word):
    x0, y0, x1, y1 = rect
    draw.rectangle(rect, fill=NAVY_SOFT)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 16
    r = 52
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=3)
    draw.ellipse([cx - r // 3, cy - r, cx + r // 3, cy + r],
                 outline=GOLD, width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=GOLD, width=2)
    draw.line([cx, cy - r, cx, cy + r], fill=GOLD, width=2)
    f = load_font(SANS_B, 23)
    w = draw.textlength(word, font=f)
    draw.text((cx - w / 2, cy + r + 12), word, font=f, fill=CREAM)


def render(data):
    page = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(page)
    edge = 28

    # Masthead
    d.rectangle([0, 0, SIZE, 148], fill=NAVY)
    spaced_text(d, SIZE // 2, 15, data["tagline"], load_font(SANS_B, 24),
                GOLD, 6)
    title_f = load_font(SERIF, 72)
    tw = d.textlength(data["paper"], font=title_f)
    d.text(((SIZE - tw) / 2, 50), data["paper"], font=title_f, fill=CREAM)
    d.rectangle([0, 148, SIZE, 152], fill=GOLD)

    # Date line, large and centred
    date_f = load_font(SERIF, 46)
    dw = d.textlength(data["date_line"], font=date_f)
    d.text(((SIZE - dw) / 2, 164), data["date_line"], font=date_f, fill=NAVY)
    d.line([edge, 226, SIZE - edge, 226], fill=NAVY, width=2)

    # Lead stories: three columns
    gap = 20
    col = (SIZE - 2 * edge - 2 * gap) // 3
    img_top, img_bot = 242, 452
    lead_f = load_font(SERIF, 26)
    for i, story in enumerate(data["lead_stories"]):
        x = edge + i * (col + gap)
        rect = (x, img_top, x + col, img_bot)
        if story["photo"]:
            cover_into(page, os.path.join(ROOT, story["photo"]), rect)
        else:
            globe_panel(d, rect, story["panel"] or "NEWS")
        y = img_bot + 12
        for line in wrap_text(d, story["headline"], lead_f, col, 5):
            d.text((x, y), line, font=lead_f, fill=INK)
            y += 33

    # Around the World grid
    d.line([edge, 640, SIZE - edge, 640], fill=RULE_TAN, width=2)
    sec_f = load_font(SANS_B, 23)
    d.text((edge, 652), "A R O U N D   T H E   W O R L D", font=sec_f,
           fill=NAVY)
    d.line([edge, 688, SIZE - edge, 688], fill=NAVY, width=2)

    cell = (SIZE - 2 * edge - gap) // 2
    grid_f = load_font(SERIF, 21)
    for idx, story in enumerate(data["world_grid"]):
        gx = edge + (idx % 2) * (cell + gap)
        gy = 702 + (idx // 2) * 118
        cover_into(page, os.path.join(ROOT, story["photo"]),
                   (gx, gy, gx + 148, gy + 100))
        tx = gx + 162
        y = gy + 1
        for line in wrap_text(d, story["headline"], grid_f,
                              gx + cell - tx, 4):
            d.text((tx, y), line, font=grid_f, fill=INK)
            y += 27

    # By the Numbers strip
    band_top, band_bot = 940, 992
    d.rectangle([0, band_top, SIZE, band_bot], fill=NAVY)
    lab_f = load_font(SANS_B, 15)
    d.text((edge, band_top + 10), "BY THE", font=lab_f, fill=GOLD)
    d.text((edge, band_top + 29), "NUMBERS", font=lab_f, fill=GOLD)
    fig_f = load_font(SERIF, 30)
    cap_f = load_font(SANS, 12)
    stats_x = 150
    stat_w = (SIZE - edge - stats_x) // 4
    for i, item in enumerate(data["figures"]):
        x = stats_x + i * stat_w
        d.text((x, band_top + 11), item["figure"], font=fig_f, fill=CREAM)
        fw = d.textlength(item["figure"], font=fig_f)
        cap_lines = wrap_text(d, item["caption"], cap_f,
                              stat_w - int(fw) - 14, 3)
        cy = band_top + 13
        for line in cap_lines:
            d.text((x + fw + 8, cy), line, font=cap_f, fill=CREAM)
            cy += 15

    # Sources footer
    foot_f = load_font(SANS, 15)
    fw = d.textlength(data["sources_footer"], font=foot_f)
    d.text(((SIZE - fw) / 2, 1000), data["sources_footer"], font=foot_f,
           fill=FAINT)

    return page


def main():
    with open(os.path.join(ROOT, "sources.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    render(data).save(os.path.join(ROOT, "entry.png"))
    print("wrote entry.png")


if __name__ == "__main__":
    main()
