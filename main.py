"""The World in One Image - 23 November 2026.

A newspaper front page drawn with nothing but the Python standard library.
Six stories from 23 November 2026, each with a headline, a short deck and a
small pictogram built from lines, circles and rectangles. No network, no
clock, no randomness: every run writes identical bytes.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (250, 246, 236)
INK = (30, 30, 32)
RED = (178, 34, 34)
BLUE = (31, 80, 140)
GOLD = (176, 132, 32)
GREY = (112, 110, 104)
SEA = (36, 110, 130)
SMOKE = (122, 120, 114)
ORANGE = (214, 110, 30)
DARKGREY = (70, 70, 74)

# A 5x7 bitmap font, drawn from scratch. Each glyph is seven rows of five
# bits, most significant bit on the left.
GLYPHS = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b11110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": (0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    ":": (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    "-": (0, 0, 0, 0b01110, 0, 0, 0),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    '"': (0b01010, 0b01010, 0, 0, 0, 0, 0),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "$": (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "+": (0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0),
    "=": (0, 0, 0b11111, 0, 0b11111, 0, 0),
    "_": (0, 0, 0, 0, 0, 0, 0b11111),
    "*": (0, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0),
    "<": (0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010),
    ">": (0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000),
    "#": (0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010),
    "@": (0b01110, 0b10001, 0b10111, 0b10101, 0b10110, 0b10000, 0b01110),
}


class Sheet:
    """An RGB canvas kept as one flat byte string, three bytes per pixel."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                xa = max(x, 0)
                xb = min(x + w, self.w)
                if xb > xa:
                    i = (yy * self.w + xa) * 3
                    self.px[i:i + (xb - xa) * 3] = bytes(c) * (xb - xa)

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.dot(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, c)

    def ring(self, cx, cy, r, c, step=2):
        for deg in range(0, 360, step):
            a = math.radians(deg)
            self.dot(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), c)

    def tri(self, p0, p1, p2, c):
        xs = [p0[0], p1[0], p2[0]]
        ys = [p0[1], p1[1], p2[1]]
        d = ((p1[1] - p2[1]) * (p0[0] - p2[0])
             + (p2[0] - p1[0]) * (p0[1] - p2[1]))
        if d == 0:
            return
        for y in range(min(ys), max(ys) + 1):
            for x in range(min(xs), max(xs) + 1):
                a = ((p1[1] - p2[1]) * (x - p2[0])
                     + (p2[0] - p1[0]) * (y - p2[1])) / d
                b = ((p2[1] - p0[1]) * (x - p2[0])
                     + (p0[0] - p2[0]) * (y - p2[1])) / d
                if a >= 0 and b >= 0 and (1 - a - b) >= 0:
                    self.dot(x, y, c)

    def glyph(self, ch, x, y, s, c):
        rows = GLYPHS.get(ch.upper(), GLYPHS[" "])
        for r in range(7):
            bits = rows[r]
            for col in range(5):
                if (bits >> (4 - col)) & 1:
                    self.rect(x + col * s, y + r * s, s, s, c)

    def text(self, txt, x, y, sc, c):
        for ch in txt:
            self.glyph(ch, x, y, sc, c)
            x += 6 * sc
        return x

    def text_w(self, txt, sc):
        return len(txt) * 6 * sc

    def para(self, txt, x, y, maxw, sc, c):
        """Word-wrap a paragraph; returns the y just below the last line."""
        words = txt.split(" ")
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if self.text_w(trial, sc) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        for ln in lines:
            self.text(ln, x, y, sc, c)
            y += 9 * sc
        return y


def _chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def save_png(path, sheet):
    ihdr = struct.pack(">IIBBBBB", sheet.w, sheet.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = sheet.w * 3
    for y in range(sheet.h):
        raw.append(0)
        raw += sheet.px[y * stride:(y + 1) * stride]
    blob = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(blob)


# ---- pictograms: one small scene per story ----

def pic_globe(s, x, y, w, h):
    """A cracked globe: the climate talks fall apart."""
    cx, cy = x + w // 2, y + h // 2
    r = min(w, h) // 2 - 4
    s.disc(cx, cy, r, (208, 228, 238))
    s.ring(cx, cy, r, BLUE)
    for dy in (-r // 2, 0, r // 2):
        dx = int(math.sqrt(r * r - dy * dy))
        s.hline(cx - dx, cy + dy, 2 * dx + 1, BLUE)
    for dx in (-r // 2, r // 2):
        dy = int(math.sqrt(r * r - dx * dx))
        s.vline(cx + dx, cy - dy, 2 * dy + 1, BLUE)
    pts = [(cx - r + 4, cy - r // 3), (cx - r // 3, cy + r // 4),
           (cx, cy - r // 4), (cx + r // 3, cy + r // 3),
           (cx + r - 4, cy - r // 5)]
    for a, b in zip(pts, pts[1:]):
        s.line(a[0], a[1], b[0], b[1], RED)
        s.line(a[0], a[1] + 1, b[0], b[1] + 1, RED)


def pic_tanker(s, x, y, w, h):
    """A tanker on fire in the strait."""
    for k in range(3):
        s.hline(x + 6, y + h - 18 - k * 8, w - 12, SEA)
    hy = y + h - 46
    s.rect(x + 14, hy, w - 28, 22, INK)
    s.tri((x + w - 14, hy), (x + w - 2, hy + 11), (x + w - 14, hy + 22), INK)
    s.rect(x + 30, hy - 16, 34, 16, RED)
    s.rect(x + 70, hy - 16, 34, 16, GOLD)
    s.rect(x + 110, hy - 16, 34, 16, BLUE)
    fx = x + 87
    s.tri((fx - 10, hy - 16), (fx, hy - 44), (fx + 10, hy - 16), ORANGE)
    s.tri((fx - 5, hy - 16), (fx, hy - 32), (fx + 5, hy - 16), RED)
    s.disc(x + 87, hy - 52, 7, SMOKE)
    s.disc(x + 96, hy - 62, 5, SMOKE)


def pic_capsize(s, x, y, w, h):
    """A warship listing hard, a small drone overhead."""
    for k in range(3):
        s.hline(x + 6, y + h - 14 - k * 8, w - 12, SEA)
    hx, hy = x + w // 2, y + h - 40
    s.tri((hx - 90, hy), (hx + 80, hy - 26), (hx + 90, hy + 2), INK)
    s.line(hx + 30, hy - 22, hx + 52, hy - 58, INK)
    dx, dy = x + w - 70, y + 18
    s.rect(dx - 8, dy - 4, 16, 8, DARKGREY)
    s.disc(dx - 12, dy - 8, 3, INK)
    s.disc(dx + 12, dy - 8, 3, INK)
    s.line(hx - 70, hy + 10, hx - 60, hy + 22, SEA)
    s.line(hx + 60, hy + 8, hx + 70, hy + 20, SEA)


def pic_flats(s, x, y, w, h):
    """A residential block, smoke rising from a damaged corner."""
    bx, by = x + 20, y + h - 70
    s.rect(bx, by, 90, 70, DARKGREY)
    for r in range(4):
        for c in range(3):
            col = GOLD if (r + c) % 2 else PAPER
            s.rect(bx + 10 + c * 26, by + 8 + r * 16, 12, 10, col)
    s.tri((bx + 90, by), (bx + 90, by + 22), (bx + 68, by), RED)
    s.disc(bx + 78, by - 14, 9, SMOKE)
    s.disc(bx + 88, by - 30, 7, SMOKE)
    s.disc(bx + 70, by - 44, 5, SMOKE)
    s.rect(bx + 110, by + 18, 60, 52, GREY)


def pic_mercury(s, x, y, w, h):
    """Cratered Mercury and the probe that just arrived."""
    cx, cy = x + 70, y + h // 2 + 6
    r = 46
    s.disc(cx, cy, r, (168, 164, 156))
    s.ring(cx, cy, r, DARKGREY)
    for ox, oy, cr in ((-16, -12, 8), (10, 6, 11), (-6, 18, 6), (18, -18, 5)):
        s.disc(cx + ox, cy + oy, cr, (140, 136, 128))
    px, py = x + w - 120, y + 22
    s.rect(px, py, 34, 20, GOLD)
    s.rect(px - 34, py + 4, 30, 12, BLUE)
    s.rect(px + 38, py + 4, 30, 12, BLUE)
    s.line(px + 17, py + 20, px + 17, py + 34, INK)
    s.disc(px + 17, py + 38, 4, RED)


def pic_factory(s, x, y, w, h):
    """A sawtooth-roof factory, flame and smoke from the roof."""
    by = y + h - 34
    bx = x + 16
    for k in range(3):
        x0 = bx + k * 56
        s.tri((x0, by), (x0 + 28, by - 26), (x0 + 56, by), INK)
    s.rect(bx, by, 168, 34, DARKGREY)
    s.rect(bx + 180, by - 52, 18, 86, INK)
    fx = bx + 84
    s.tri((fx - 12, by - 20), (fx, by - 52), (fx + 12, by - 20), ORANGE)
    s.tri((fx - 6, by - 20), (fx, by - 38), (fx + 6, by - 20), RED)
    s.disc(bx + 189, by - 62, 8, SMOKE)
    s.disc(bx + 198, by - 76, 6, SMOKE)
    s.rect(bx + 70, by + 16, 24, 18, PAPER)


# ---- layout ----

def half_box(s, x, y, w, h, kicker, headline, deck, pic):
    s.frame(x, y, w, h, INK, 2)
    ix = x + 16
    s.text(kicker, ix, y + 12, 1, RED)
    s.text(headline, ix, y + 30, 2, INK)
    s.para(deck, ix, y + 54, w - 32, 1, INK)
    pic(s, ix, y + 104, w - 32, h - 116)


def draw_page(s):
    s.rect(0, 0, W, H, PAPER)
    s.hline(36, 26, W - 72, INK, 2)
    title = "THE WORLD IN ONE IMAGE"
    s.text(title, (W - s.text_w(title, 5)) // 2, 40, 5, INK)
    date = "MONDAY, 23 NOVEMBER 2026"
    s.text(date, (W - s.text_w(date, 2)) // 2, 88, 2, INK)
    s.hline(36, 116, W - 72, INK, 4)
    s.hline(36, 124, W - 72, INK, 2)

    # Lead story: the climate summit collapses.
    s.frame(36, 136, 952, 196, INK, 2)
    s.text("CLIMATE SUMMIT", 52, 148, 1, RED)
    s.text("COP31 COLLAPSES WITH NO DEAL", 52, 166, 3, INK)
    s.para("CLIMATE TALKS END WITHOUT AGREEMENT AS THE EU REFUSES "
           "ANY TEXT WITH NO FOSSIL FUEL PHASE-OUT", 52, 206, 560, 1, INK)
    s.text("EU: NO PHASE-OUT, NO DEAL", 52, 232, 1, RED)
    pic_globe(s, 640, 148, 332, 170)

    # Second row: the strait and the corvette.
    half_box(s, 36, 348, 466, 208, "STRAIT OF HORMUZ",
             "TANKERS HIT AS WAR SPREADS",
             "TWO MORE TANKERS CATCH FIRE ON MINES AS THE WAR REACHES "
             "SAUDI ARABIA AND BAHRAIN", pic_tanker)
    half_box(s, 522, 348, 466, 208, "BLACK SEA",
             "SEA DRONES SINK CORVETTE",
             "UKRAINIAN SEA DRONES STRIKE THE RUSSIAN CORVETTE AT "
             "BENGHAZI. THE SHIP CAPSIZES. 10 INJURED.", pic_capsize)

    # Third row: the drone strike and the space probe.
    half_box(s, 36, 572, 466, 208, "UKRAINE",
             "DRONE HITS FLATS IN DYMER",
             "A RUSSIAN DRONE HITS A RESIDENTIAL BLOCK NORTH OF KYIV. "
             "2 KILLED, 11 MISSING.", pic_flats)
    half_box(s, 522, 572, 466, 208, "SPACE",
             "BEPICOLOMBO REACHES MERCURY",
             "THE EUROPEAN-JAPANESE PROBE ENTERS ORBIT AROUND MERCURY, "
             "ONLY THE SECOND MISSION EVER TO DO SO.", pic_mercury)

    # Bottom strip: the factory fire.
    s.frame(36, 796, 952, 172, INK, 2)
    s.text("INDONESIA", 52, 808, 1, RED)
    s.text("FACTORY FIRE IN CIKANDE: 24 DEAD", 52, 826, 2, INK)
    s.para("RESCUERS RECOVER 24 BODIES AFTER A CANDY FACTORY FIRE IN "
           "CIKANDE, BANTEN.", 52, 852, 560, 1, INK)
    pic_factory(s, 640, 808, 332, 148)

    foot = "SIX STORIES FROM ONE DAY - 23 NOVEMBER 2026"
    s.text(foot, (W - s.text_w(foot, 1)) // 2, 984, 1, GREY)


def main():
    s = Sheet(W, H, PAPER)
    draw_page(s)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    save_png(os.path.join(out, "entry.png"), s)


if __name__ == "__main__":
    main()
