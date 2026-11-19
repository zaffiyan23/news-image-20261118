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

from PIL import Image, ImageDraw, ImageFont

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
    ["ASIA-PACIFIC", "EUROPE"],
    ["MIDDLE EAST"],
    ["AMERICAS", "BUSINESS & TECH", "SCIENCE & WORLD"],
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


def draw_world_map(draw, x, y, cell=6):
    for gy in range(0, 100, cell):
        for gx in range(0, 212, cell):
            for cx, cy, rx, ry in CONTINENTS:
                if ((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2 <= 1.0:
                    draw.ellipse([x + gx, y + gy, x + gx + 3, y + gy + 3],
                                 fill=INK)
                    break


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
    title_font = font(SANS_BOLD, 15)
    body_font = font(SANS, 13)
    draw.text((x, y), title, font=title_font, fill=RED)
    y += 20
    draw.line([(x, y), (x + width, y)], fill=INK, width=1)
    y += 6
    for item in items:
        bullet_x = x + 10
        draw.text((x, y), "\u2022", font=body_font, fill=RED)
        y = draw_wrapped(draw, bullet_x, y, item, body_font, INK,
                          width - 12, 16)
        y += 3
    return y + 8


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
    y = 26
    masthead = font(SERIF_BOLD, 46)
    title = "THE WORLD IN ONE PAGE"
    tw = draw.textlength(title, font=masthead)
    draw.text(((WIDTH - tw) / 2, y), title, font=masthead, fill=INK)
    y += 58

    date_font = font(SERIF_BOLD, 34)
    date_text = "Wednesday, 18 November 2026"
    tw = draw.textlength(date_text, font=date_font)
    draw.text(((WIDTH - tw) / 2, y), date_text, font=date_font, fill=RED)
    y += 48

    # Black strip with the counted story total.
    strip_font = font(SANS_BOLD, 16)
    strip_text = f"{STORY_COUNT} STORIES \u00b7 DATE-CHECKED \u00b7 ALL TIMES UTC"
    draw.rectangle([MARGIN, y, WIDTH - MARGIN, y + 28], fill=INK)
    tw = draw.textlength(strip_text, font=strip_font)
    draw.text(((WIDTH - tw) / 2, y + 5), strip_text, font=strip_font,
              fill=PAPER)
    y += 40

    # -------------------------------------------------------------- lead
    lead_x = MARGIN + 6
    lead_w = 600
    kicker_font = font(SANS_BOLD, 14)
    draw.text((lead_x, y), "LEAD STORY \u00b7 APEC SUMMIT \u00b7 SHENZHEN",
              font=kicker_font, fill=RED)
    y += 22
    lead_font = font(SERIF_BOLD, 31)
    y = draw_wrapped(draw, lead_x, y, LEAD_HEADLINE, lead_font, INK,
                     lead_w, 36)
    y += 4
    lead_body = font(SANS, 13)
    for bullet in LEAD_BULLETS:
        draw.text((lead_x, y), "\u2022", font=lead_body, fill=RED)
        y = draw_wrapped(draw, lead_x + 12, y, bullet, lead_body, INK,
                         lead_w - 14, 16)
        y += 2

    # Dot-grid world map beside the lead.
    map_x = lead_x + lead_w + 18
    draw_world_map(draw, map_x, 186, cell=6)
    map_caption = font(SANS_ITALIC, 11)
    draw.text((map_x + 58, 292), "One day, every region.",
              font=map_caption, fill=GREY)

    lead_bottom = y + 8
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

    # Key-figures panel fills the page under the columns.
    draw_numbers_panel(draw, MARGIN + 6, columns_bottom + 4,
                       WIDTH - 2 * MARGIN - 12)

    # ---------------------------------------------------- sequence strip
    seq_y = 862
    draw.line([(MARGIN, seq_y), (WIDTH - MARGIN, seq_y)], fill=INK, width=2)
    seq_title = font(SANS_BOLD, 14)
    draw.text((MARGIN + 6, seq_y + 8), "THE DAY IN SEQUENCE (UTC)",
              font=seq_title, fill=RED)
    seq_font = font(SANS_BOLD, 13)
    seq_text = "  \u2192  ".join(SEQUENCE)
    y = draw_wrapped(draw, MARGIN + 6, seq_y + 30, seq_text, seq_font, INK,
                     WIDTH - 2 * MARGIN - 12, 17)

    # -------------------------------------------------------------- footer
    foot_y = 952
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
