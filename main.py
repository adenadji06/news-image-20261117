#!/usr/bin/env python3
"""news-image-20261117: one image summing up Tuesday 17 November 2026.

Draws a newspaper front page (1024x1024) in pure Python stdlib:
own PNG encoder (zlib+struct), own 5x7 bitmap font, own rasteriser,
own simplified world map. No network, no files read, deterministic:
two runs write byte-identical PNGs.
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (178, 32, 44)
BLUE = (31, 78, 121)
GREY = (110, 105, 95)
LIGHT = (226, 219, 203)
OCEAN = (207, 227, 238)
LAND = (232, 220, 192)
LAND_EDGE = (150, 132, 90)
PIN_BG = (255, 255, 255)
GOLD = (176, 132, 32)

# ------------------------------------------------------- PNG encoder (stdlib)
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(rgb, w, h):
    """rgb: bytes of w*h*3. Returns a complete PNG file (filter 0 rows)."""
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", idat) + _chunk(b"IEND", b""))


# ------------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 rows of 5 bits, written as strings. Uppercase only; lowercase
# input is upper-cased before drawing (newspaper headline style).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, max_chars):
    """Greedy word wrap; returns list of lines, each <= max_chars."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, color)
                else:
                    if r * r - 2 * r <= d <= r * r:
                        self.set(xx, yy, color)

    def polygon(self, pts, color):
        """Scanline fill of a simple polygon (list of (x, y))."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            nodes = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    nodes.append(int(x0 + (y - y0) * (x1 - x0) / (y1 - y0)))
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                for x in range(nodes[k], nodes[k + 1] + 1):
                    self.set(x, y, color)

    def polyline(self, pts, color):
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            self.line(x0, y0, x1, y1, color)

    def draw_text(self, x, y, text, scale, color, align="left"):
        text = text.upper()
        w = text_width(text, scale)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return w

    def text_block(self, x, y, text, scale, color, max_chars, leading=None):
        """Wrapped text; returns y after the last line."""
        if leading is None:
            leading = 7 * scale + 3
        for line in wrap_text(text, max_chars):
            self.draw_text(x, y, line, scale, color)
            y += leading
        return y


# ------------------------------------------------- simplified world continents
# Rough (lon, lat) outlines, equirectangular projection. Deliberately
# simplified: recognisable at front-page scale, no disputed borders drawn.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
     (-125, 40), (-125, 48), (-135, 58), (-155, 58), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-22, 70), (-25, 76),
     (-40, 80), (-58, 76), (-62, 70)],
    # South America
    [(-80, 9), (-75, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-65, -41), (-70, -50),
     (-74, -54), (-73, -44), (-72, -30), (-70, -18), (-77, -12), (-80, -5),
     (-81, 1)],
    # Africa
    [(-17, 15), (-10, 30), (-5, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 2), (40, -5), (40, -15), (35, -25), (28, -33),
     (18, -35), (12, -18), (9, 4), (-8, 5), (-15, 11)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 66), (40, 68),
     (44, 68), (48, 66), (50, 60), (45, 55), (40, 50), (35, 46), (30, 46),
     (28, 44), (23, 40), (19, 42), (12, 44), (8, 44), (3, 43), (-2, 44)],
    # Asia (incl. Siberia north coast)
    [(30, 36), (35, 36), (36, 42), (40, 42), (44, 39), (48, 39), (50, 37),
     (54, 37), (57, 26), (58, 25), (61, 25), (66, 25), (70, 23), (72, 20),
     (77, 8), (80, 7), (80, 13), (85, 19), (89, 22), (91, 22), (93, 16),
     (95, 16), (98, 10), (100, 8), (103, 1), (104, 9), (106, 11), (109, 13),
     (108, 18), (106, 20), (108, 21), (110, 20), (114, 22), (116, 23),
     (120, 25), (122, 28), (120, 32), (122, 37), (124, 40), (127, 40),
     (130, 42), (132, 43), (135, 44), (137, 46), (140, 46), (142, 50),
     (142, 54), (141, 59), (142, 59), (156, 51), (158, 53), (160, 55),
     (162, 56), (163, 60), (170, 60), (178, 65), (178, 68), (170, 66),
     (162, 66), (158, 70), (155, 70), (150, 72), (145, 72), (140, 72),
     (135, 72), (130, 71), (125, 73), (120, 73), (115, 73), (110, 74),
     (105, 76), (100, 77), (95, 76), (90, 75), (85, 74), (80, 73),
     (75, 72), (70, 72), (65, 69), (60, 69), (55, 68), (52, 68), (50, 68),
     (48, 66), (44, 68), (40, 68)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (140, 37),
     (141, 39), (141, 41), (142, 42), (143, 43), (145, 44), (141, 45),
     (140, 44), (139, 40), (137, 37), (134, 34), (131, 33)],
    # Indonesia (thin archipelago strip)
    [(95, 5), (98, 4), (100, 0), (102, -2), (104, -3), (106, -6), (108, -7),
     (110, -7), (112, -7), (114, -8), (116, -8), (119, -9), (120, -10),
     (122, -9), (124, -9), (126, -8), (128, -4), (130, -2), (132, -1),
     (135, -2), (137, -3), (140, -4), (141, -3)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Australia
    [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (140, -17), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14),
     (122, -17), (118, -20), (114, -22)],
]


# ------------------------------------------------------------ the day's news
# Every item was first reported on Tuesday 17 November 2026 (sources in
# the build notes). Headlines are plain statements of what was reported;
# nothing here is speculation, and nothing predates 13 Nov 2026.
LEADS = [
    ("KERCH BRIDGE SPAN FALLS AFTER UKRAINIAN STRIKE",
     "Zelenskyy hails 'unprecedented operation' weeks in the making; "
     "Kremlin vows to rebuild. Russia hits Kyiv bridges in reply."),
    ("TRUMP LANDS IN MANILA AS ASIA TRIP OPENS",
     "US-Thailand trade statement signed in Manila; three-way talks "
     "with Xi and Putin set for Shenzhen on Thursday."),
    ("TWO TANKERS HIT MINES IN STRAIT OF HORMUZ",
     "Iran's Revolutionary Guards say the tankers caught fire; the "
     "claim is unverified. A third US carrier arrives in the region."),
]

# (number, section, headline, deck, pin lon/lat or None, pin offset)
STORIES = [
    (4, "MIDDLE EAST", "IRAN DRONES TARGET US RADAR IN BAHRAIN",
     "No casualties reported.", 50.5, 26.2, -18, 12),
    (5, "MIDDLE EAST", "US STRIKES IRGC LAUNCH SITE ON QESHM",
     "Tehran denies damage.", 55.5, 27.0, 18, 14),
    (6, "MIDDLE EAST", "UK SANCTIONS 8 ISRAELI SETTLEMENT FIRMS",
     "Two-state bid defended.", -0.1, 51.5, -26, -18),
    (7, "MIDDLE EAST", "WEST URGES ISRAEL TO OPEN GAZA AID CROSSINGS",
     "Nations demand aid now.", 34.5, 31.5, -14, 14),
    (8, "MIDDLE EAST", "HOUTHIS ADVANCE AS YEMEN FORCES RETREAT",
     "Troops defend Aden now.", 45.0, 12.8, 0, 0),
    (9, "EUROPE", "DEPARDIEU ADMITS SEXUAL ASSAULT IN PARIS COURT",
     "Guilty plea entered.", 2.3, 48.9, 26, -14),
    (10, "EUROPE", "EU CHARGES TEMU OVER ILLEGAL PRODUCT SALES",
     "EU: too little done.", 4.4, 50.8, 24, 16),
    (11, "ASIA-PACIFIC", "JAPAN SCRAMBLES JETS OVER INCURSION",
     "Tokyo lodges protest.", 139.7, 35.7, 0, 0),
    (12, "ASIA-PACIFIC", "MONGOLIA PRESIDENT TO STEP DOWN",
     "Amid corruption claims.", 106.9, 47.9, 0, 0),
    (13, "ASIA-PACIFIC", "TURKEY TAKES SOZCU TV OFF AIR AFTER RAID",
     "Raid silences channel.", 32.9, 39.9, 24, 6),
    (14, "ASIA-PACIFIC", "CANADA AND CHINA AGREE TO EXPAND TRADE",
     "Tariffs cut both ways.", -75.7, 45.4, -20, -30),
    (15, "MARKETS & TECH", "NVIDIA BEATS: $115.8BN QUARTER, GUIDES $130BN",
     "Shares jump late today.", -122.0, 37.4, -16, -14),
    (16, "MARKETS & TECH", "NASDAQ IN CORRECTION AS STOCKS SLIDE AGAIN",
     "Second day of losses.", -74.0, 40.7, 0, -24),
    (17, "MARKETS & TECH", "US CURBS CHINA'S ACCESS TO AI CHIPS",
     "Curbs hit data centres.", -77.0, 38.9, -26, 16),
    (18, "AMERICAS", "US LOSES MEASLES ELIMINATION STATUS",
     "Most cases since 1991.", -74.0, 40.7, 26, -20),
    (19, "AMERICAS", "SUPREME COURT REJECTS TRUMP DEI GRANT APPEAL",
     "$60m cuts stand.", -77.0, 38.9, -28, -22),
    (20, "AMERICAS", "HOUSE DEMOCRATS SET OPENING AGENDA",
     "Health care leads list.", -77.0, 38.9, 26, 6),
    (21, "AMERICAS", "MAMDANI DISBANDS NOTORIOUS NYPD UNIT",
     "Mayor ends the unit.", -74.0, 40.7, -8, 24),
    (22, "SPORT & CULTURE", "RAYE LEADS GRAMMY NODS WITH 11",
     "Ties Beyonce's record.", -118.2, 34.0, 16, 12),
    (23, "SPORT & CULTURE", "SPACEX CATCHES STARSHIP AFTER ORBITAL FLIGHT",
     "A first for Starship.", -97.2, 25.9, 0, 0),
    (24, "SPORT & CULTURE", "PATTINSON NAMED NEXT JAMES BOND",
     "Pattinson named as 007.", -0.1, 51.5, -28, 16),
]

# Lead-story pins on the map (number shown on the pin is the lead index).
LEAD_PINS = [(1, 34.0, 45.0, 0, -16), (2, 121.0, 14.6, 0, 0),
             (3, 56.5, 26.3, 0, -16)]

SECTIONS = ["MIDDLE EAST", "EUROPE", "ASIA-PACIFIC",
            "MARKETS & TECH", "AMERICAS", "SPORT & CULTURE"]
# columns: (x, [sections...])
COLUMNS = [
    (24, ["MIDDLE EAST", "EUROPE"]),
    (356, ["ASIA-PACIFIC", "MARKETS & TECH"]),
    (688, ["AMERICAS", "SPORT & CULTURE"]),
]
COL_W = 312
COL_TOP = 584
COL_BOTTOM = 998


def draw_map(cv, x, y, w, h):
    """Stylised world map with numbered pins for the day's stories."""
    cv.rect(x, y, w, h, OCEAN)
    cv.rect(x, y, w, 2, INK)
    cv.rect(x, y + h - 2, w, 2, INK)
    cv.rect(x, y, 2, h, INK)
    cv.rect(x + w - 2, y, 2, h, INK)

    def proj(lon, lat):
        px = x + int((lon + 180.0) / 360.0 * w)
        py = y + int((72.0 - lat) / 122.0 * h)
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        cv.polygon(pts, LAND)
        cv.polyline(pts, LAND_EDGE)

    cv.draw_text(x + 10, y + 8, "WHERE IT HAPPENED", 2, BLUE)
    cv.draw_text(x + w - 10, y + 8, "17 NOV 2026", 2, BLUE, align="right")

    def pin(num, lon, lat, dx=0, dy=0, color=RED):
        px, py = proj(lon, lat)
        tx, ty = px, py
        px += dx
        py += dy
        if dx or dy:
            cv.line(tx, ty, px, py, color)
            cv.circle(tx, ty, 2, color)
        cv.circle(px, py, 10, color)
        cv.circle(px, py, 10, INK, fill=False)
        cv.circle(px, py, 9, PIN_BG)
        cv.circle(px, py, 9, color, fill=False)
        label = str(num)
        tw = text_width(label, 1)
        cv.draw_text(px - tw // 2, py - 3, label, 1, INK)

    for num, lon, lat, dx, dy in LEAD_PINS:
        pin(num, lon, lat, dx, dy)
    for (num, _sec, _h, _d, lon, lat, dx, dy) in STORIES:
        if lon is not None:
            pin(num, lon, lat, dx, dy)


def draw_story(cv, x, y, num, headline, deck, max_w_chars):
    """One numbered story entry. Returns y after the entry."""
    # number badge
    cv.rect(x, y, 22, 16, RED)
    label = str(num)
    tw = text_width(label, 1)
    cv.draw_text(x + (22 - tw) // 2, y + 4, label, 1, (255, 255, 255))
    hx = x + 30
    y = cv.text_block(hx, y, headline, 2, INK, max_w_chars, leading=15)
    y = cv.text_block(hx, y + 1, deck, 2, GREY, max_w_chars, leading=15)
    return y + 4


def draw_section(cv, x, y, title):
    cv.draw_text(x, y, title, 2, RED)
    cv.hline(x, y + 18, COL_W, RED, 2)
    return y + 27


def build():
    cv = Canvas(W, H, PAPER)
    # thin outer frame
    cv.rect(0, 0, W, 4, INK)
    cv.rect(0, H - 4, W, 4, INK)
    cv.rect(0, 0, 4, H, INK)
    cv.rect(W - 4, 0, 4, H, INK)

    # ---- masthead
    cv.draw_text(W // 2, 16, "THE WORLD IN ONE DAY", 5, INK, align="center")
    cv.draw_text(W // 2, 58, "TUESDAY 17 NOVEMBER 2026", 4, RED, align="center")
    cv.hline(24, 96, W - 48, INK, 3)

    # ---- lead story (full width)
    y = 106
    y = cv.text_block(24, y, LEADS[0][0], 3, INK, 52, leading=26)
    y = cv.text_block(24, y + 2, LEADS[0][1], 2, GREY, 78)
    cv.hline(24, y + 6, W - 48, LIGHT, 2)
    y += 14
    # ---- second row: two half-width leads
    half = (W - 48 - 24) // 2
    y0 = y
    y1 = cv.text_block(24, y0, LEADS[1][0], 2, INK, 38)
    y1 = cv.text_block(24, y1 + 1, LEADS[1][1], 2, GREY, 38)
    y2 = cv.text_block(24 + half + 24, y0, LEADS[2][0], 2, INK, 38)
    y2 = cv.text_block(24 + half + 24, y2 + 1, LEADS[2][1], 2, GREY, 38)
    y = max(y1, y2) + 8

    # ---- map
    map_h = COL_TOP - y - 12
    draw_map(cv, 24, y, W - 48, map_h)

    # ---- story columns
    max_chars = (COL_W - 30) // 12  # scale-2 chars after the number badge
    for col_x, sections in COLUMNS:
        cy = COL_TOP
        for sec in sections:
            cy = draw_section(cv, col_x, cy, sec)
            for (num, s2, head, deck, _lo, _la, _dx, _dy) in STORIES:
                if s2 != sec:
                    continue
                cy = draw_story(cv, col_x, cy, num, head, deck, max_chars)
                if cy > COL_BOTTOM:
                    break
            cy += 4

    # ---- footer
    cv.hline(24, COL_BOTTOM + 6, W - 48, INK, 2)
    cv.draw_text(24, COL_BOTTOM + 12,
                 "ALL STORIES FIRST REPORTED TUESDAY 17 NOVEMBER 2026",
                 1, GREY)
    cv.draw_text(W - 24, COL_BOTTOM + 12, "24 STORIES - 6 REGIONS",
                 1, GREY, align="right")
    return bytes(cv.px)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build(), W, H)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
