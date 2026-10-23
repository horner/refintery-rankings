#!/usr/bin/env python3
"""Draw the 1200 × 630 link-preview cards: one per team page and one for the home page.

Reads the built dist/data.json, so run broadcast/scripts/build.py first. Needs Pillow, which the
offline build and CI do not; the cards are committed like the display images. Each card records a
fingerprint of the facts drawn on it, and verify.py fails when the data has moved on.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from share_facts import card_facts, fingerprint, home_facts

HERE = Path(__file__).resolve().parents[1]
DIST = HERE / "dist"
FONTS = DIST / "assets/fonts"
W, H = 1200, 630
NAVY, DEEP, INK, GREEN, MINT, WHITE, MUTED = "#134b70", "#0d3550", "#0f172a", "#40a578", "#a1d18b", "#ffffff", "#b9c6d2"


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def fit(draw, text, name, size, width):
    """Largest size up to `size` at which `text` fits in `width`."""
    while size > 20 and draw.textlength(text, font=font(name, size)) > width:
        size -= 2
    return font(name, size)


def logo_image(team, display):
    for kind in ("team", "school"):
        mark = (team.get("logos") or {}).get(kind) or {}
        path = display.get(mark.get("file"), {}).get("file") or mark.get("file")
        if path and not path.endswith(".svg"):
            return Image.open(DIST / path).convert("RGBA"), mark.get("background") == "dark"
    return None, False


def team_card(team, program, display, out):
    facts = card_facts(team, program)
    image = Image.new("RGB", (W, H), DEEP)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, 14, H], fill=GREEN)
    for i, color in enumerate((GREEN, NAVY, MINT)):
        draw.rectangle([i * W // 3, H - 12, (i + 1) * W // 3, H], fill=color)
    draw.text((64, 52), f"NORTHEAST INDIANA ROBOTICS · {'2026 SEASON' if program == 'FRC' else 'FTC 2026–27'}", font=font("barlow-condensed-latin-700.woff2", 30), fill=MINT)
    # Logo tile on the right; a number tile when only a vector mark exists.
    logo, dark = logo_image(team, display)
    box = (W - 64 - 300, 120, W - 64, 420)
    draw.rectangle(box, fill=DEEP if dark else WHITE)
    if logo:
        fitted = ImageOps.contain(logo, (260, 260))
        image.paste(fitted, (box[0] + (300 - fitted.width) // 2, box[1] + (300 - fitted.height) // 2), fitted)
    else:
        number = str(facts["number"])
        draw.rectangle(box, fill=NAVY)
        f = fit(draw, number, "barlow-condensed-latin-800-italic.woff2", 140, 260)
        draw.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), number, font=f, fill=WHITE, anchor="mm")
    text_width = box[0] - 64 - 40
    name = facts["name"].upper()
    draw.text((64, 108), name, font=fit(draw, name, "barlow-condensed-latin-800-italic.woff2", 116, text_width), fill=WHITE)
    draw.text((64, 238), f"{facts['program']} {facts['number']}", font=font("barlow-condensed-latin-700.woff2", 40), fill=MINT)
    subline = f"{facts['school']} · {facts['city']}".strip(" ·")
    draw.text((64, 288), subline, font=fit(draw, subline, "inter-latin-wght.woff2", 28, text_width), fill=MUTED)
    x = 64
    for value, label in facts["stats"]:
        draw.text((x, 360), value, font=font("barlow-condensed-latin-800.woff2", 84), fill=WHITE)
        draw.text((x, 452), label.upper(), font=font("barlow-condensed-latin-700.woff2", 22), fill=MUTED)
        x += max(draw.textlength(value, font=font("barlow-condensed-latin-800.woff2", 84)), draw.textlength(label.upper(), font=font("barlow-condensed-latin-700.woff2", 22))) + 56
    honors = "  /  ".join(h.upper() for h in facts["honors"])
    if honors:
        draw.text((64, 520), honors, font=fit(draw, honors, "barlow-condensed-latin-700.woff2", 32, W - 128), fill="#e2b04a")
    draw.text((W - 64, 520), "THE REFINERY", font=font("barlow-condensed-latin-800.woff2", 32), fill=WHITE, anchor="ra")
    image.save(out, "PNG", optimize=True)
    return fingerprint(facts)


def home_card(data, out):
    photo = Image.open(DIST / "assets/photos/fans-4982.webp").convert("RGB")
    image = ImageOps.fit(photo, (W, H), centering=(0.5, 0.35))
    shade = Image.new("RGBA", (W, H))
    shade_draw = ImageDraw.Draw(shade)
    for x in range(W):  # Navy on the left fading to a dark tint, like the hero.
        shade_draw.line([(x, 0), (x, H)], fill=(13, 53, 80, int(235 - 120 * x / W)))
    image = Image.alpha_composite(image.convert("RGBA"), shade).convert("RGB")
    draw = ImageDraw.Draw(image)
    for i, color in enumerate((GREEN, NAVY, MINT)):
        draw.rectangle([i * W // 3, H - 12, (i + 1) * W // 3, H], fill=color)
    lines = [("THE ONLY SPORT", WHITE), ("WHERE EVERY KID", WHITE), ("CAN GO PRO.", MINT)]
    for i, (line, color) in enumerate(lines):
        draw.text((64, 110 + i * 112), line, font=font("barlow-condensed-latin-800-italic.woff2", 124), fill=color)
    s = data["seasonSummary"]
    draw.text((64, 470), "NORTHEAST INDIANA HIGH SCHOOL ROBOTICS", font=font("barlow-condensed-latin-700.woff2", 36), fill=WHITE)
    draw.text((64, 520), f"{s['teams']} FRC TEAMS  /  {s['eventTitles']} EVENT TITLES  /  {len(s['worldsTeams'])} WORLD CHAMPIONSHIP TEAMS",
              font=font("barlow-condensed-latin-700.woff2", 28), fill=MINT)
    image.save(out, "JPEG", quality=84, optimize=True, progressive=True)
    return fingerprint(home_facts(data))


def main():
    data = json.loads((DIST / "data.json").read_text(encoding="utf-8"))
    folder = DIST / "assets/share"
    folder.mkdir(parents=True, exist_ok=True)
    rows = {"home": {"file": "assets/share/home.jpg", "fingerprint": home_card(data, folder / "home.jpg")}}
    for program, teams in (("FRC", data["standings"]), ("FTC", data["ftc"]["teams"] + data["ftc"]["newTeams"])):
        for team in teams:
            name = f"team-{team['number']}.png"
            rows[str(team["number"])] = {"file": f"assets/share/{name}", "fingerprint": team_card(team, program, data["displayAssets"], folder / name)}
    (HERE / "data/share-images.json").write_text(json.dumps({"generator": "broadcast/scripts/build_share_images.py", "cards": rows}, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} share cards to {folder}")


if __name__ == "__main__":
    main()
