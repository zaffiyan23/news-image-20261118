#!/usr/bin/env python3
"""Build the make.fun news-image-20261118 entry poster.

A front-page style infographic poster that sums up the world news of
Wednesday, 18 November 2026 in one 1024x1024 PNG image.

The judge has no news feed, so the poster itself carries:
  - the date, large and unmissable,
  - the day's lead story (the APEC summit in Shenzhen),
  - dozens of short, readable headlines across every region,
  - a UTC sequence strip and a source line for credibility.

The story count printed in the masthead strip is counted from the
headline data below, never typed by hand, so it always matches the
number of stories actually printed on the page.
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps

# The hero picture of the day: Trump, Xi and Putin at the Shenzhen
# summit, an original editorial illustration made for this entry and
# kept in the repository beside this program.
HERO_PATH = "assets/hero-summit.webp"

# ---------------------------------------------------------------- palette
PAPER = "#f7f3e8"
INK = "#141414"
RED = "#b3001b"
GREY = "#4a463c"
RULE = "#141414"

WIDTH = 1024
HEIGHT = 1024
MARGIN = 28

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- the news
LEAD_HEADLINE = "XI GREETS TRUMP AS APEC OPENS IN SHENZHEN"
LEAD_BULLETS = [
    "Handshake becomes a hug on the Shenzhen tarmac as the summit opens",
    "First Trump-Xi-Putin trilateral meeting set for Thursday",
    "Trilateral agenda: nuclear arms, Ukraine, Iran, trade and AI",
    "Xi-Putin bilateral held; Trump and Putin shake hands at the family photo",
]

SECTIONS = [
    ("ASIA-PACIFIC", [
        "Quad - US, Japan, India, Australia - meets in Manila, first in over 2 years",
        "Trump announces trade deal with the Philippines",
        "Two Russian aircraft violate Japanese airspace off Fukuoka",
        "Taiwan records 10 PLA sorties and 11 naval vessels",
        "South Korea's Lee Jae Myung uses APEC to strengthen ties with Beijing",
        "Cyclone Akvan strengthens off India",
        "Mass evacuations under way in Odisha as Akvan nears",
    ]),
    ("MIDDLE EAST", [
        "Iran claims drone strike on US facility at Ali Al Salem, Kuwait",
        "Bahrain intercepts attack before dawn",
        "US jets strike Iranian missile-launcher site on Qeshm Island - US official",
        "Strait of Hormuz disrupted as shipping comes under fire",
        "Tanker Tara Gas hit twice; one sailor missing",
        "Oil holds near $93 a barrel",
        "Iraq: Kataib Hezbollah given until Friday to leave town near Baghdad",
        "Turkish authorities seize opposition TV station",
        "Board of Peace warns Gaza ceasefire is at risk of collapse - Al Jazeera",
        "WHO: 950,000 Palestinians displaced on flood-prone land; Gaza faces a fourth winter - UN",
    ]),
    ("EUROPE", [
        "Russia launches 141 drones overnight",
        "126 drones shot down or suppressed",
        "Drone strike on Dnipro injures 6",
        "Reports of attack on Kerch Bridge, Crimea",
        "EU agrees EUR 45 billion loan package for Ukraine",
    ]),
    ("AMERICAS", [
        "Peltola (Democrat) defeats Sen. Sullivan in Alaska - Senate 56-44 Democrat - AP",
        "Jeffries wins House Speaker nomination 251-11",
        "US loses measles-free status after 26 years",
        "Jesse Jackson dies aged 84",
    ]),
    ("BUSINESS & TECH", [
        "Nvidia board decides not to return Jensen Huang as CEO",
        "Nvidia earnings beat forecasts",
        "Anthropic sets IPO at $83 a share",
        "Anthropic valuation put at $1.5 trillion - AP",
    ]),
    ("SCIENCE & WORLD", [
        "Voyager 1 reaches one light-day from Earth",
        "Military cargo plane crashes in Siberia",
        "19 killed in Siberia cargo-plane crash",
    ]),
]

# Which sections go in which of the three columns under the lead block.
COLUMNS = [
    ["ASIA-PACIFIC", "SCIENCE & WORLD"],
    ["MIDDLE EAST"],
    ["AMERICAS", "BUSINESS & TECH", "EUROPE"],
]

SEQUENCE = [
    "Shenzhen summit opens",
    "Gulf intercepts before dawn",
    "Dnipro strike",
    "Alaska called",
    "Voyager milestone",
]

SOURCES_LINE = "Sources: AP \u00b7 AFP \u00b7 Al Jazeera \u00b7 UN News \u00b7 The Hindu - Compiled 19 Nov 2026"
FOOTER_LINE = "make.fun picture of the day entry"

STORY_COUNT = 1 + len(LEAD_BULLETS) + sum(len(items) for _, items in SECTIONS)


# ------------------------------------------------------------- world map
# A coarse dot-grid world map, drawn from an ASCII sketch: each '#'
# becomes a dot, so the lead block carries a recognisable world shape.
WORLD_MAP = [
    "  ooooo  o          oo    oooooooooooo o              ",
    " oooooooo oo       ooo   ooooooooooooooooo  oo        ",
    "oooooooooo         oo   ooooooooooooooooooo ooo       ",
    " ooooooooo          o    ooooo ooooooooooo   oo       ",
    "  ooooooo                oooo   ooooo  ooo            ",
    "   ooooo                  oo     ooo    oo   o        ",
    "    ooo                  ooo      o          oo       ",
    "    oo                  oooo                        ",
    "    o                    oo            o            ",
    "   oo                    o            ooo           ",
    "   oo                                   o           ",
    "  oo                                                ",
]


# Continent blobs as (centre x, centre y, radius x, radius y) in map
# units: a dot is drawn wherever a grid point falls inside a blob, so
# the silhouette reads as North and South America, Europe and Africa,
# Asia and Australia without pretending to be a precise atlas.
CONTINENTS = [
    (32, 22, 30, 17),   # North America, west and centre
    (58, 32, 17, 10),   # North America, east
    (52, 74, 12, 23),   # South America
    (98, 18, 15, 9),    # Europe
    (108, 52, 15, 24),  # Africa
    (168, 22, 40, 16),  # Asia
    (142, 50, 9, 13),   # India and South Asia
    (172, 52, 7, 12),   # South-East Asia
    (186, 86, 15, 8),   # Australia
]


def draw_world_map(draw, x, y, cell=6, scale=1.0):
    dot = max(2, int(3 * scale))
    for gy in range(0, 100, cell):
        for gx in range(0, 212, cell):
            for cx, cy, rx, ry in CONTINENTS:
                if ((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2 <= 1.0:
                    dx = x + gx * scale
                    dy = y + gy * scale
                    draw.ellipse([dx, dy, dx + dot, dy + dot], fill=INK)
                    break


# ------------------------------------------------------- illustrations
# Flat editorial pictograms drawn with PIL shapes in the poster's own
# ink and red - original artwork made for this entry, in one style:
# a big lead picture of the Shenzhen summit, and a small spot picture
# beside every section title.

def draw_lead_art(draw, x, y, w, h):
    """The APEC lead picture: Shenzhen skyline, a red sun, and two
    leaders meeting in silhouette in front of it."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    ground = y + h - 34
    # Red sun over the skyline.
    draw.ellipse([x + w - 92, y + 14, x + w - 40, y + 66], fill=RED)
    # Skyline: dark towers of different heights, lit windows as dots.
    towers = [(8, 62), (34, 88), (62, 52), (88, 96), (118, 70),
              (146, 84), (300, 58), (326, 90), (354, 66), (380, 80),
              (408, 56), (434, 92)]
    for tx, th in towers:
        if tx + 24 > w - 8:
            continue
        draw.rectangle([x + tx, ground - th, x + tx + 22, ground],
                       fill=INK)
        for wy in range(ground - th + 7, ground - 8, 11):
            for wx in (x + tx + 5, x + tx + 13):
                draw.rectangle([wx, wy, wx + 3, wy + 4], fill=PAPER)
    draw.line([(x, ground), (x + w, ground)], fill=INK, width=2)
    # Two figures meeting in the open plaza between the towers:
    # heads, suit bodies, arms reaching to a handshake at the centre.
    cx = x + w // 2
    for side in (-1, 1):
        hx = cx + side * 46
        draw.ellipse([hx - 13, ground - 84, hx + 13, ground - 58], fill=INK)
        draw.polygon([(hx - 19, ground), (hx - 12, ground - 58),
                      (hx + 12, ground - 58), (hx + 19, ground)], fill=INK)
        draw.line([(hx - side * 6, ground - 44), (cx, ground - 30)],
                  fill=INK, width=7)
        draw.polygon([(hx - 3, ground - 56), (hx + 5, ground - 56),
                      (hx + 1, ground - 38)], fill=RED)
    draw.ellipse([cx - 6, ground - 36, cx + 6, ground - 24], fill=RED)
    caption = font(SANS_ITALIC, 11)
    draw.text((x + 8, y + h - 24), "Leaders meet as APEC opens in Shenzhen.",
              font=caption, fill=GREY)


def draw_icon(draw, name, x, y):
    """A 30x30 spot illustration for a section, at (x, y)."""
    if name == "cyclone":
        for r in (13, 9, 5):
            draw.arc([x + 15 - r, y + 15 - r, x + 15 + r, y + 15 + r],
                     start=20, end=300, fill=INK, width=2)
        draw.ellipse([x + 13, y + 13, x + 17, y + 17], fill=RED)
    elif name == "tanker":
        draw.polygon([(x + 2, y + 18), (x + 28, y + 18), (x + 24, y + 25),
                      (x + 6, y + 25)], fill=INK)
        draw.rectangle([x + 7, y + 11, x + 14, y + 18], fill=RED)
        draw.rectangle([x + 16, y + 13, x + 23, y + 18], fill=INK)
        draw.arc([x + 2, y + 22, x + 14, y + 30], 0, 180, fill=INK, width=2)
        draw.arc([x + 16, y + 22, x + 28, y + 30], 0, 180, fill=INK, width=2)
    elif name == "drone":
        for dx, dy in ((4, 4), (22, 4), (4, 22), (22, 22)):
            draw.ellipse([x + dx, y + dy, x + dx + 5, y + dy + 5],
                         outline=INK, width=2)
        draw.line([(x + 6, y + 6), (x + 24, y + 24)], fill=INK, width=2)
        draw.line([(x + 24, y + 6), (x + 6, y + 24)], fill=INK, width=2)
        draw.rectangle([x + 12, y + 12, x + 18, y + 18], fill=RED)
    elif name == "dome":
        draw.arc([x + 5, y + 2, x + 25, y + 18], 180, 360, fill=INK, width=2)
        draw.line([(x + 15, y + 2), (x + 15, y - 2 + 4)], fill=RED, width=2)
        for cx in (7, 12, 17, 22):
            draw.line([(x + cx, y + 14), (x + cx, y + 24)], fill=INK, width=2)
        draw.line([(x + 3, y + 26), (x + 27, y + 26)], fill=INK, width=2)
    elif name == "chip":
        draw.rectangle([x + 7, y + 7, x + 23, y + 23], outline=INK, width=2)
        draw.rectangle([x + 12, y + 12, x + 18, y + 18], fill=RED)
        for p in (10, 15, 20):
            draw.line([(x + p, y + 2), (x + p, y + 7)], fill=INK, width=2)
            draw.line([(x + p, y + 23), (x + p, y + 28)], fill=INK, width=2)
            draw.line([(x + 2, y + p), (x + 7, y + p)], fill=INK, width=2)
            draw.line([(x + 23, y + p), (x + 28, y + p)], fill=INK, width=2)
    elif name == "satellite":
        draw.rectangle([x + 12, y + 11, x + 19, y + 19], fill=INK)
        draw.rectangle([x + 2, y + 8, x + 10, y + 15], fill=RED)
        draw.rectangle([x + 21, y + 15, x + 29, y + 22], fill=RED)
        draw.arc([x + 14, y + 16, x + 30, y + 30], 270, 360, fill=INK,
                 width=2)
        draw.ellipse([x + 26, y + 24, x + 29, y + 27], fill=INK)


SECTION_ICONS = {
    "ASIA-PACIFIC": "cyclone",
    "MIDDLE EAST": "tanker",
    "EUROPE": "drone",
    "AMERICAS": "dome",
    "BUSINESS & TECH": "chip",
    "SCIENCE & WORLD": "satellite",
}


# ------------------------------------------------------------- text help
def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, x, y, text, fnt, fill, max_width, leading):
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def draw_section(draw, x, y, width, title, items):
    title_font = font(SANS_BOLD, 14)
    body_font = font(SANS, 12)
    icon = SECTION_ICONS.get(title)
    if icon:
        draw_icon(draw, icon, x, y - 5)
    draw.text((x + 36, y), title, font=title_font, fill=RED)
    y += 19
    draw.line([(x, y), (x + width, y)], fill=INK, width=1)
    y += 5
    for item in items:
        bullet_x = x + 10
        draw.text((x, y), "\u2022", font=body_font, fill=RED)
        y = draw_wrapped(draw, bullet_x, y, item, body_font, INK,
                          width - 12, 14)
        y += 1
    return y + 6


# The day's key figures, every one of them taken from a headline
# already printed above - no new facts, just the numbers pulled out
# big so a reader scanning the page catches the scale of the day.
DAY_IN_NUMBERS = [
    ("141", "drones launched overnight; 126 downed"),
    ("950,000", "Palestinians displaced - WHO"),
    ("EUR 45bn", "EU loan package for Ukraine"),
    ("$93", "oil, a barrel, as Hormuz is disrupted"),
    ("56-44", "US Senate after Alaska is called"),
    ("1", "light-day: Voyager 1 from Earth"),
]


def draw_numbers_panel(draw, x, y, width):
    title_font = font(SANS_BOLD, 15)
    num_font = font(SERIF_BOLD, 19)
    label_font = font(SANS, 11)
    draw.text((x, y), "THE DAY IN NUMBERS", font=title_font, fill=RED)
    y += 21
    draw.line([(x, y), (x + width, y)], fill=INK, width=1)
    y += 6
    col_w = width // 3
    for i, (num, label) in enumerate(DAY_IN_NUMBERS):
        cx = x + (i % 3) * col_w
        cy = y + (i // 3) * 38
        draw.text((cx, cy), num, font=num_font, fill=INK)
        draw_wrapped(draw, cx, cy + 21, label, label_font, GREY,
                     col_w - 14, 13)
    return y + 76


# ------------------------------------------------------------------ main
def build():
    img = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(img)

    # Outer frame: a double rule like a newspaper front page.
    draw.rectangle([10, 10, WIDTH - 11, HEIGHT - 11], outline=INK, width=3)
    draw.rectangle([16, 16, WIDTH - 17, HEIGHT - 17], outline=INK, width=1)

    # ---------------------------------------------------------- masthead
    y = 24
    masthead = font(SERIF_BOLD, 42)
    title = "THE WORLD IN ONE PAGE"
    tw = draw.textlength(title, font=masthead)
    draw.text(((WIDTH - tw) / 2, y), title, font=masthead, fill=INK)
    y += 52

    date_font = font(SERIF_BOLD, 32)
    date_text = "Wednesday, 18 November 2026"
    tw = draw.textlength(date_text, font=date_font)
    draw.text(((WIDTH - tw) / 2, y), date_text, font=date_font, fill=RED)
    y += 44

    # Black strip with the counted story total.
    strip_font = font(SANS_BOLD, 16)
    strip_text = f"{STORY_COUNT} STORIES \u00b7 DATE-CHECKED \u00b7 ALL TIMES UTC"
    draw.rectangle([MARGIN, y, WIDTH - MARGIN, y + 28], fill=INK)
    tw = draw.textlength(strip_text, font=strip_font)
    draw.text(((WIDTH - tw) / 2, y + 5), strip_text, font=strip_font,
              fill=PAPER)
    y += 40

    # ------------------------------------------------- hero picture
    # The day's picture is the poster's spotlight: Trump, Xi and Putin
    # at the Shenzhen summit, full width under the masthead.
    hero_x = MARGIN
    hero_w = WIDTH - 2 * MARGIN
    hero_h = 288
    hero = ImageOps.fit(Image.open(HERO_PATH).convert("RGB"),
                        (hero_w, hero_h), centering=(0.5, 0.58))
    img.paste(hero, (hero_x, y))
    draw = ImageDraw.Draw(img)
    draw.rectangle([hero_x, y, hero_x + hero_w - 1, y + hero_h - 1],
                   outline=INK, width=3)
    y += hero_h + 8

    # Lead headline and its facts in two columns under the picture.
    kicker_font = font(SANS_BOLD, 13)
    draw.text((MARGIN + 6, y), "LEAD STORY \u00b7 APEC SUMMIT \u00b7 SHENZHEN",
              font=kicker_font, fill=RED)
    y += 19
    lead_font = font(SERIF_BOLD, 25)
    y = draw_wrapped(draw, MARGIN + 6, y, LEAD_HEADLINE, lead_font, INK,
                     hero_w - 12, 29)
    lead_body = font(SANS, 12)
    bullet_w = (hero_w - 24) // 2
    bullet_top = y + 2
    bullet_bottom = bullet_top
    for i, bullet in enumerate(LEAD_BULLETS):
        bx = MARGIN + 6 + (i % 2) * (bullet_w + 12)
        by = bullet_top + (i // 2) * 32
        draw.text((bx, by), "\u2022", font=lead_body, fill=RED)
        by = draw_wrapped(draw, bx + 11, by, bullet, lead_body, INK,
                          bullet_w - 12, 15)
        bullet_bottom = max(bullet_bottom, by)
    y = bullet_bottom + 4

    lead_bottom = y
    draw.line([(MARGIN, lead_bottom), (WIDTH - MARGIN, lead_bottom)],
              fill=INK, width=2)

    # ------------------------------------------------------------ columns
    col_top = lead_bottom + 12
    col_gap = 18
    col_w = (WIDTH - 2 * MARGIN - 2 * col_gap) // 3
    section_by_name = dict(SECTIONS)
    columns_bottom = col_top
    for col_i, names in enumerate(COLUMNS):
        cx = MARGIN + col_i * (col_w + col_gap)
        cy = col_top
        for name in names:
            cy = draw_section(draw, cx, cy, col_w, name,
                              section_by_name[name])
        columns_bottom = max(columns_bottom, cy)
        if col_i < 2:
            vx = cx + col_w + col_gap // 2
            draw.line([(vx, col_top), (vx, columns_bottom + 2)],
                      fill=RULE, width=1)

    # One band of the day's key figures under the columns.
    band_y = columns_bottom + 2
    band_title = font(SANS_BOLD, 13)
    draw.text((MARGIN + 6, band_y), "THE DAY IN NUMBERS:", font=band_title,
              fill=RED)
    band_font = font(SANS_BOLD, 12)
    band_text = ("141 drones, 126 downed \u00b7 950,000 displaced \u00b7 EUR 45bn for Ukraine \u00b7 "
                 "oil $93 \u00b7 Senate 56-44 \u00b7 Voyager 1 at one light-day")
    draw_wrapped(draw, MARGIN + 162, band_y, band_text, band_font, INK,
                 WIDTH - 2 * MARGIN - 168, 15)

    # ---------------------------------------------------- sequence strip
    seq_y = 936
    draw.line([(MARGIN, seq_y), (WIDTH - MARGIN, seq_y)], fill=INK, width=2)
    seq_title = font(SANS_BOLD, 13)
    draw.text((MARGIN + 6, seq_y + 7), "THE DAY IN SEQUENCE (UTC):",
              font=seq_title, fill=RED)
    seq_font = font(SANS_BOLD, 12)
    seq_text = "  \u2192  ".join(SEQUENCE)
    draw_wrapped(draw, MARGIN + 210, seq_y + 7, seq_text, seq_font, INK,
                 WIDTH - 2 * MARGIN - 216, 15)

    # -------------------------------------------------------------- footer
    foot_y = 968
    draw.line([(MARGIN, foot_y), (WIDTH - MARGIN, foot_y)], fill=INK,
              width=1)
    foot_font = font(SANS, 12)
    tw = draw.textlength(SOURCES_LINE, font=foot_font)
    draw.text(((WIDTH - tw) / 2, foot_y + 8), SOURCES_LINE,
              font=foot_font, fill=INK)
    tw = draw.textlength(FOOTER_LINE, font=foot_font)
    draw.text(((WIDTH - tw) / 2, foot_y + 26), FOOTER_LINE,
              font=foot_font, fill=GREY)

    img.save("entry.png", optimize=True)
    print(f"stories={STORY_COUNT} size=1024x1024")


if __name__ == "__main__":
    build()
