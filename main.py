"""The World in One Image - Monday 23 November 2026.

A broadsheet front page drawn entirely in code: a hand-cut 5x7 pixel
font, a small RGB canvas with its own drawing primitives, one small
pictogram per story, and a PNG writer built from struct and zlib.
Pure Python standard library only -- no network, no clock, no
randomness, no files read at run time. Every run writes the same
bytes to a deterministic 1024x1024 PNG.

Stories, all first reported on Monday 23 November 2026 (or the night
before, as the day's news round-ups carried them):
  1. COP31 climate talks collapse with no deal: the EU and others
     reject any final text that leaves out a fossil fuel phase-out.
  2. Tankers are struck in and near the Strait of Hormuz; two more
     catch fire on naval mines, and the Iran-US war reaches Saudi
     Arabia and Bahrain.
  3. Suspected Ukrainian sea drones hit the Russian corvette Merkury
     at the Benghazi naval base in Libya; the ship capsizes.
  4. A Russian drone hits a five-storey apartment block in Dymer,
     north of Kyiv; two killed, eleven missing, two of them children.
  5. After eight years in flight, the European-Japanese BepiColombo
     spacecraft enters orbit around Mercury -- only the second
     mission ever to do so.
  6. Rescuers recover 24 bodies from a candy factory fire in
     Cikande, Banten, Indonesia; dozens are still missing.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 242, 230)
PANEL = (255, 255, 255)
INK = (24, 24, 24)
RED = (168, 32, 32)
NAVY = (28, 52, 94)
TEAL = (18, 110, 96)
OCHRE = (178, 124, 32)
GOLD = (212, 175, 55)
SKY = (158, 196, 222)
GREY = (110, 110, 105)
SMOKE = (120, 116, 108)
EMBER = (214, 90, 20)

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is seven rows; each row is a five-bit
# number, its most significant bit the leftmost cell.
# ---------------------------------------------------------------------------

FONT = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8),
    "'": (4, 4, 8, 0, 0, 0, 0),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "-": (0, 0, 0, 14, 0, 0, 0),
    "/": (1, 2, 2, 4, 8, 8, 16),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 6, 4, 0, 4),
    "%": (25, 26, 2, 4, 8, 11, 19),
    "&": (12, 18, 20, 8, 21, 18, 13),
    "+": (0, 4, 4, 31, 4, 4, 0),
    '"': (10, 10, 0, 0, 0, 0, 0),
    "=": (0, 0, 31, 0, 31, 0, 0),
}

GLYPH_W = 5
GLYPH_H = 7
GLYPH_ADVANCE = 6  # glyph width plus one blank column, in font units


def text_width(text, scale):
    """Width in pixels of text drawn at the given scale."""
    return len(text) * GLYPH_ADVANCE * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    max_chars = max(1, max_width // (GLYPH_ADVANCE * scale))
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if len(trial) <= max_chars:
                line = trial
            else:
                if line:
                    lines.append(line)
                while len(word) > max_chars:
                    lines.append(word[:max_chars])
                    word = word[max_chars:]
                line = word
        if line:
            lines.append(line)
    return lines


# ---------------------------------------------------------------------------
# Tiny RGB canvas with its own drawing primitives.
# ---------------------------------------------------------------------------

class Canvas:
    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def set_px(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i] = colour[0]
            self.pixels[i + 1] = colour[1]
            self.pixels[i + 2] = colour[2]

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            row = bytes(colour) * (x1 - x0)
            self.pixels[base:base + (x1 - x0) * 3] = row

    def rect(self, x, y, w, h, colour, thickness=1):
        self.fill_rect(x, y, w, thickness, colour)
        self.fill_rect(x, y + h - thickness, w, thickness, colour)
        self.fill_rect(x, y, thickness, h, colour)
        self.fill_rect(x + w - thickness, y, thickness, h, colour)

    def hline(self, x, y, w, colour, thickness=1):
        self.fill_rect(x, y, w, thickness, colour)

    def vline(self, x, y, h, colour, thickness=1):
        self.fill_rect(x, y, thickness, h, colour)

    def line(self, x0, y0, x1, y1, colour):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_px(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, colour):
        """Midpoint circle outline."""
        x = 0
        y = r
        d = 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set_px(px, py, colour)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def fill_circle(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            half = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.fill_rect(cx - half, yy, half * 2 + 1, 1, colour)

    def triangle(self, x0, y0, x1, y1, x2, y2, colour):
        """Filled triangle by scanline."""
        points = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = points
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / (by - ay) if by != ay else 0.0
                xa = ax + (bx - ax) * t1
            else:
                t2 = (y - by) / (cy - by) if cy != by else 0.0
                xa = bx + (cx - bx) * t2
            t3 = (y - ay) / (cy - ay)
            xb = ax + (cx - ax) * t3
            lo, hi = (int(xa), int(xb)) if xa <= xb else (int(xb), int(xa))
            self.fill_rect(lo, y, hi - lo + 1, 1, colour)

    def draw_text(self, x, y, text, scale, colour):
        """Draw text; input is upper-cased, unknown glyphs become blank."""
        cx = x
        for ch in text.upper():
            rows = FONT.get(ch)
            if rows:
                for r in range(GLYPH_H):
                    bits = rows[r]
                    for c in range(GLYPH_W):
                        if (bits >> (GLYPH_W - 1 - c)) & 1:
                            self.fill_rect(cx + c * scale, y + r * scale,
                                           scale, scale, colour)
            cx += GLYPH_ADVANCE * scale
        return cx

    def draw_block(self, x, y, text, max_width, scale, colour,
                   line_gap=4):
        """Draw wrapped text; returns the y just below the last line."""
        lines = wrap_text(text, max_width, scale)
        for line in lines:
            self.draw_text(x, y, line, scale, colour)
            y += GLYPH_H * scale + line_gap
        return y


# ---------------------------------------------------------------------------
# PNG writer: colour type 2 (RGB), filter 0 on every scanline, no
# ancillary chunks, so the output is fully deterministic.
# ---------------------------------------------------------------------------

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        start = y * stride
        raw += canvas.pixels[start:start + stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.width,
                                       canvas.height, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------------------
# Pictograms, one per story. Each draws inside a small box (x, y, w, h).
# ---------------------------------------------------------------------------

def draw_cracked_globe(c, x, y, w, h):
    """A globe split by a crack, with a crossed-out oil drop: COP31."""
    cx, cy = x + w // 2 - 20, y + h // 2
    r = min(w, h) // 2 - 4
    c.fill_circle(cx, cy, r, SKY)
    c.circle(cx, cy, r, INK)
    c.fill_circle(cx - r // 3, cy - r // 4, r // 3, TEAL)
    c.fill_circle(cx + r // 3, cy + r // 4, r // 4, TEAL)
    c.fill_circle(cx + r // 5, cy - r // 2, r // 5, TEAL)
    # Jagged crack down the middle of the globe.
    crack = [(cx - 4, cy - r), (cx + 6, cy - r // 2), (cx - 6, cy),
             (cx + 6, cy + r // 2), (cx - 4, cy + r)]
    for (ax, ay), (bx, by) in zip(crack, crack[1:]):
        c.line(ax, ay, bx, by, INK)
        c.line(ax + 1, ay, bx + 1, by, INK)
    # Oil drop with a red cross-out, to the right of the globe.
    dx, dy = x + w - 58, y + h // 2 - 26
    c.triangle(dx, dy + 8, dx - 16, dy + 34, dx + 16, dy + 34, INK)
    c.fill_circle(dx, dy + 34, 16, INK)
    c.circle(dx, dy + 18, 30, RED)
    c.line(dx - 21, dy - 3, dx + 21, dy + 39, RED)
    c.line(dx - 20, dy - 3, dx + 20, dy + 39, RED)
    c.line(dx - 21, dy - 4, dx + 21, dy + 38, RED)


def draw_tanker(c, x, y, w, h):
    """An oil tanker on a strait, smoke rising, a mine below."""
    sea = y + h - 16
    c.fill_rect(x, sea, w, h - (sea - y), SKY)
    # Hull and bow.
    c.fill_rect(x + 8, sea - 16, w - 16, 16, NAVY)
    c.fill_rect(x + 8, sea - 16, w - 16, 4, RED)
    c.triangle(x + w - 8, sea - 16, x + w + 10, sea - 2,
               x + w - 8, sea, NAVY)
    # Bridge tower and funnel.
    c.fill_rect(x + w - 70, sea - 34, 36, 18, PANEL)
    c.rect(x + w - 70, sea - 34, 36, 18, INK, 2)
    c.fill_rect(x + w - 62, sea - 28, 20, 5, INK)
    c.fill_rect(x + 24, sea - 30, 18, 14, OCHRE)
    # Smoke curling from the funnel.
    c.fill_circle(x + 33, sea - 36, 5, SMOKE)
    c.fill_circle(x + 41, sea - 44, 6, SMOKE)
    # Flame licking the deck.
    c.triangle(x + 96, sea - 16, x + 104, sea - 34, x + 112, sea - 16,
               EMBER)
    c.triangle(x + 100, sea - 16, x + 104, sea - 28, x + 108, sea - 16,
               GOLD)
    # A spiked naval mine drifting below the hull.
    mx, my = x + 40, sea + 8
    c.fill_circle(mx, my, 6, INK)
    c.line(mx - 8, my, mx + 8, my, INK)
    c.line(mx, my - 8, mx, my + 8, INK)


def draw_warship(c, x, y, w, h):
    """A warship listing to one side, a drone skimming above it."""
    sea = y + h - 14
    c.fill_rect(x, sea, w, h - (sea - y), SKY)
    # Hull and bow.
    c.fill_rect(x + 14, sea - 14, w - 28, 14, NAVY)
    c.fill_rect(x + 14, sea - 14, w - 28, 4, RED)
    c.triangle(x + w - 14, sea - 14, x + w + 6, sea - 2,
               x + w - 14, sea, NAVY)
    # Superstructure and mast.
    c.fill_rect(x + w // 2 - 24, sea - 30, 56, 16, GREY)
    c.rect(x + w // 2 - 24, sea - 30, 56, 16, INK, 2)
    c.fill_rect(x + w // 2 + 6, sea - 44, 8, 14, INK)
    c.fill_rect(x + w // 2 - 4, sea - 48, 28, 4, INK)
    # Smoke pouring from the deck.
    c.fill_circle(x + w // 2 - 40, sea - 36, 6, SMOKE)
    c.fill_circle(x + w // 2 - 52, sea - 44, 7, SMOKE)
    # A small sea drone with a wake, top left.
    c.fill_rect(x + 16, y + 4, 30, 8, INK)
    c.fill_circle(x + 46, y + 8, 5, INK)
    c.line(x + 16, y + 12, x + 2, y + 20, SKY)


def draw_ruined_block(c, x, y, w, h):
    """A five-storey block with its corner blown out, rubble below."""
    bx, by = x + w // 2 - 40, y + 2
    bw, bh = 80, h - 16
    c.fill_rect(bx, by, bw, bh, (196, 188, 172))
    c.rect(bx, by, bw, bh, INK, 2)
    # Lit windows on the intact floors.
    for row in range(2):
        for col in range(3):
            wx = bx + 8 + col * 24
            wy = by + 8 + row * 14
            c.fill_rect(wx, wy, 10, 9, GOLD)
            c.rect(wx, wy, 10, 9, INK, 1)
    # The blown-out corner: dark hole.
    c.fill_rect(bx + bw - 26, by + bh - 16, 26, 16, INK)
    c.triangle(bx + bw - 26, by + bh - 16, bx + bw - 12, by + bh - 6,
               bx + bw - 26, by + bh - 4, (196, 188, 172))
    # Rubble mound at the base.
    base = by + bh
    c.triangle(bx - 12, base, bx + 2, base - 10, bx + 16, base, GREY)
    c.triangle(bx + 30, base, bx + 48, base - 12, bx + 66, base, GREY)
    # A drone silhouette above the roof.
    c.fill_rect(x + w - 34, y + 2, 20, 5, INK)
    c.hline(x + w - 40, y, 32, INK, 2)


def draw_probe(c, x, y, w, h):
    """BepiColombo: a spacecraft with long solar wings near Mercury."""
    cx, cy = x + w // 2 + 10, y + h // 2
    # Mercury, cratered, bottom left.
    mx, my = x + 18, y + h - 14
    c.fill_circle(mx, my, 12, OCHRE)
    c.fill_circle(mx - 4, my - 3, 3, (150, 100, 24))
    c.fill_circle(mx + 4, my + 2, 2, (150, 100, 24))
    # Stars.
    c.fill_rect(x + w - 24, y + 6, 3, 3, INK)
    c.fill_rect(x + w - 52, y + 16, 3, 3, INK)
    # Solar wings.
    c.fill_rect(cx - 70, cy - 8, 52, 16, NAVY)
    c.fill_rect(cx + 18, cy - 8, 52, 16, NAVY)
    for wx in range(cx - 70, cx - 18, 10):
        c.vline(wx, cy - 8, 16, (120, 150, 200), 2)
    for wx in range(cx + 18, cx + 70, 10):
        c.vline(wx, cy - 8, 16, (120, 150, 200), 2)
    # Bus and dish.
    c.fill_rect(cx - 18, cy - 12, 36, 24, PANEL)
    c.rect(cx - 18, cy - 12, 36, 24, INK, 2)
    c.fill_rect(cx - 6, cy - 4, 12, 8, GOLD)
    c.triangle(cx - 18, cy - 12, cx - 32, cy - 22, cx - 18, cy - 22, INK)
    # Orbit arc sweeping past Mercury.
    c.line(mx + 10, my - 12, cx - 44, cy + 18, GREY)
    c.line(cx - 44, cy + 18, cx + 30, cy + 24, GREY)


def draw_factory_fire(c, x, y, w, h):
    """A factory shed with flames and a column of smoke."""
    base = y + h - 8
    # Shed with a sawtooth roof.
    c.fill_rect(x + 14, base - 26, w - 28, 26, (150, 142, 128))
    c.rect(x + 14, base - 26, w - 28, 26, INK, 2)
    c.triangle(x + 14, base - 26, x + 14 + (w - 28) // 3, base - 34,
               x + 14 + 2 * (w - 28) // 3, base - 26, INK)
    c.triangle(x + 14 + (w - 28) // 3, base - 26,
               x + 14 + 2 * (w - 28) // 3, base - 34,
               x + w - 14, base - 26, INK)
    # Flames bursting from the roofline.
    for fx, fh in ((x + 36, 16), (x + 70, 20), (x + 104, 16)):
        c.triangle(fx, base - 26, fx + 9, base - 26 - fh,
                   fx + 18, base - 26, EMBER)
        c.triangle(fx + 5, base - 26, fx + 9, base - 26 - fh + 8,
                   fx + 13, base - 26, GOLD)
    # Smoke column rising to the top of the box.
    c.fill_circle(x + w // 2, y + 6, 6, SMOKE)
    c.fill_circle(x + w // 2 + 10, y + 14, 7, SMOKE)
    c.fill_circle(x + w // 2 - 6, y + 22, 8, SMOKE)
    # Door and a broken window.
    c.fill_rect(x + w // 2 - 10, base - 18, 20, 18, INK)
    c.fill_rect(x + 26, base - 22, 14, 10, GOLD)
    c.line(x + 26, base - 22, x + 40, base - 12, INK)
    c.line(x + 40, base - 22, x + 26, base - 12, INK)


# ---------------------------------------------------------------------------
# Page layout.
# ---------------------------------------------------------------------------

MARGIN = 28
CONTENT_W = WIDTH - 2 * MARGIN


def panel(c, x, y, w, h):
    c.fill_rect(x, y, w, h, PANEL)
    c.rect(x, y, w, h, INK, 2)


def story_block(c, x, y, w, h, kicker, headline, body,
                head_scale=3, body_scale=2, art=None, art_h=0):
    """One story: red kicker, headline, body text, art pinned to the
    bottom of the panel so text can never run over it."""
    inner = x + 16
    width = w - 32
    c.draw_text(inner, y + 12, kicker, 2, RED)
    yy = c.draw_block(inner, y + 34, headline, width, head_scale, INK, 3)
    c.draw_block(inner, yy + 4, body, width, body_scale, INK, 4)
    if art is not None:
        art(c, x + 16, y + h - art_h - 8, width, art_h)


def build_page():
    c = Canvas(WIDTH, HEIGHT, PAPER)

    # Masthead.
    title = "THE WORLD IN ONE IMAGE"
    c.draw_text((WIDTH - text_width(title, 5)) // 2, 30, title, 5, INK)
    c.hline(MARGIN, 82, CONTENT_W, INK, 3)
    date = "MONDAY 23 NOVEMBER 2026"
    c.draw_text((WIDTH - text_width(date, 3)) // 2, 96, date, 3, RED)
    sub = "SIX STORIES THAT SHAPED THE DAY"
    c.draw_text((WIDTH - text_width(sub, 2)) // 2, 128, sub, 2, INK)
    c.hline(MARGIN, 152, CONTENT_W, INK, 6)

    # Lead story: COP31 collapses.
    ly, lh = 168, 252
    panel(c, MARGIN, ly, CONTENT_W, lh)
    tx = MARGIN + 20
    tw = 540
    c.draw_text(tx, ly + 18, "CLIMATE - COP31", 2, RED)
    y = c.draw_block(tx, ly + 46, "Climate talks collapse",
                     tw, 5, INK, 4)
    y = c.draw_block(tx, y + 2,
                     "No deal in Turkiye. The EU and others reject "
                     "any text without a fossil fuel phase-out.",
                     tw, 3, INK, 5)
    c.draw_block(tx, y + 6, "Talks end with no agreement.",
                 tw, 3, INK, 5)
    draw_cracked_globe(c, MARGIN + 600, ly + 16,
                       CONTENT_W - 620, lh - 32)

    # Middle row: the Strait of Hormuz and the Benghazi strike.
    my, mh = 436, 232
    mw = (CONTENT_W - 16) // 2
    panel(c, MARGIN, my, mw, mh)
    story_block(
        c, MARGIN, my, mw, mh, "STRAIT OF HORMUZ",
        "Tankers struck in Hormuz",
        "Three tankers are hit near the strait and two more catch "
        "fire on mines. The war reaches Saudi Arabia.",
        art=draw_tanker, art_h=64)
    panel(c, MARGIN + mw + 16, my, mw, mh)
    story_block(
        c, MARGIN + mw + 16, my, mw, mh, "LIBYA",
        "Warship hit in Benghazi",
        "Suspected Ukrainian sea drones hit the Russian corvette "
        "Merkury at the naval base. The ship capsizes; 10 injured.",
        art=draw_warship, art_h=64)

    # Bottom row: Ukraine, Mercury, Indonesia.
    by, bh = 684, 216
    bw = (CONTENT_W - 26) // 3
    panel(c, MARGIN, by, bw, bh)
    story_block(
        c, MARGIN, by, bw, bh, "UKRAINE",
        "Drone hits Kyiv flats",
        "A Russian drone hits a block in Dymer, near Kyiv. Two "
        "killed, 11 missing.",
        head_scale=2, art=draw_ruined_block, art_h=56)
    panel(c, MARGIN + bw + 13, by, bw, bh)
    story_block(
        c, MARGIN + bw + 13, by, bw, bh, "SPACE",
        "Mercury gains a visitor",
        "BepiColombo enters Mercury orbit after eight years in "
        "flight -- only the second ever.",
        head_scale=2, art=draw_probe, art_h=56)
    panel(c, MARGIN + 2 * bw + 26, by, bw, bh)
    story_block(
        c, MARGIN + 2 * bw + 26, by, bw, bh, "INDONESIA",
        "Factory fire in Banten",
        "Rescuers recover 24 bodies from a candy factory fire in "
        "Cikande. Dozens are still missing.",
        head_scale=2, art=draw_factory_fire, art_h=56)

    # Footer.
    c.hline(MARGIN, 914, CONTENT_W, INK, 3)
    foot = "DRAWN ENTIRELY IN CODE - NO PHOTOGRAPHS - MAKE.FUN NEWS-IMAGE-20261123"
    c.draw_text((WIDTH - text_width(foot, 2)) // 2, 930, foot, 2, INK)
    foot2 = "MONDAY 23 NOVEMBER 2026 - SIX STORIES, ONE PAGE"
    c.draw_text((WIDTH - text_width(foot2, 2)) // 2, 958, foot2, 2, GREY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    page = build_page()
    write_png(page, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
