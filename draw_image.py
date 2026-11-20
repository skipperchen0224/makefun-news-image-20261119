#!/usr/bin/env python3
"""Draw the 19 November 2026 world-news front page (1024x1024 PNG), v2.

News facts verified against live reporting on 19 Nov 2026 (AP, Reuters,
AFP, NYT, WSJ, NDTV, Japan Times, Just Security). All copy lives in the
NEWS dict below, so the page can be re-skinned for another day by
replacing that dict (see README).

Layout: masthead, banner lead (full-width, 56px extra-bold), then a
3-column grid where the Myanmar story spans two columns and GTA VI spans
two columns beside a mini crossword. Halftone-dot photo placeholders,
line-art icons, old-paper texture and a vignette finish the newsprint
look.

Deterministic: every random choice comes from random.Random(seed); the
same seed always writes identical bytes (no timestamps, no network).
Every block is measured before it is drawn; asserts guard overflow.
"""
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1024, 1024
M = 48  # margin
SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"
SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SERIF_L = "/usr/share/fonts/truetype/noto/NotoSerif-Light.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS_I = "/usr/share/fonts/truetype/noto/NotoSans-Italic.ttf"

PAPER = (244, 241, 234)      # old paper #F4F1EA
INK = (26, 26, 26)
BODY = (74, 74, 74)
FAINT = (122, 122, 122)
RED = (139, 0, 0)
HAIR = (208, 200, 184)      # column rules #D0C8B8
PHOTO_BG = (232, 230, 224)

# ---------------------------------------------------------------- news ---
# (kicker, headline, body, sources). Replace this dict to re-skin the
# page for another day; the layout measures itself and asserts fit.
NEWS = {
    "lead": {
        "kicker": "EXCLUSIVE:  TOP STORY  \u2022  SHENZHEN, CHINA",
        "headline": "Trump, Xi and Putin declare peace after Shenzhen summit",
        "deck": ("The three leaders hold the first ever U.S.-China-Russia "
                 "trilateral meeting on the APEC sidelines and announce a "
                 "joint peace declaration."),
        "body": ("SHENZHEN \u2014 The leaders of the United States, China "
                 "and Russia held their first ever trilateral meeting and "
                 "announced a joint peace declaration, capping a day of "
                 "diplomacy in the southern Chinese city. The declaration "
                 "was announced after the three leaders met on the APEC "
                 "sidelines."),
        "sources": "Sources: AP, Reuters, Dawn",
    },
    "stories": [
        ("MYANMAR", "World court finds Myanmar guilty of genocide",
         "The court rules Myanmar carried out state-backed genocide "
         "against the Rohingya \u2014 a first for the UN's top court.",
         "Just Security, Japan Times"),
        ("GULF", "Iran widens strikes on Kuwait and Bahrain",
         "Three tankers catch fire after hitting mines east of the "
         "Strait of Hormuz.", "WSJ, NDTV"),
        ("RIYADH", "Houthi missile hits PIF Tower",
         "A missile strikes the Saudi wealth fund's HQ, the capital's "
         "tallest tower.", "NYT, Japan Times"),
        ("UKRAINE", "Ukraine hits Kerch Bridge a third time",
         "Kyiv strikes the Crimea bridge for the third time in four "
         "days; rail traffic halted.", "AP"),
        ("BANGLADESH", "Unrest spreads in Bangladesh",
         "The ancestral home of former leader Yunus is torched as "
         "Hasina party protests spread.", "AFP"),
        ("CULTURE & TECH", "GTA VI launches worldwide",
         "Rockstar's long-awaited game goes on sale around the world "
         "on its first day.", "NDTV"),
    ],
    "footer": ("Voyager 1 reaches one light-day from Earth "
               "(Daily Mirror) \u2014 all events of 19 November 2026."),
}


def font(path, size):
    return ImageFont.truetype(path, size)


class Page:
    """A page: crisp rules/photos on the base, all text on a jittered,
    lightly blurred overlay (ink-bleed), then paper grain + vignette."""

    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.img = Image.new("RGB", (W, H), PAPER)
        self.d = ImageDraw.Draw(self.img)
        # text overlay: RGBA so the 0.5px blur softens only the type
        self.ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.t = ImageDraw.Draw(self.ov)

    # -- text (1-2px jitter from the seeded rng = letterpress wobble) --
    def text(self, xy, s, fnt, fill):
        dx = self.rng.choice((-1, 0, 0, 1))
        dy = self.rng.choice((-1, 0, 0, 1))
        self.t.text((xy[0] + dx, xy[1] + dy), s, font=fnt, fill=fill + (255,))

    def wrap(self, text, fnt, width, limit=None):
        lines, cur = [], ""
        for word in text.split():
            trial = (cur + " " + word).strip()
            if self.t.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        if limit is not None:
            assert len(lines) <= limit, (text, lines)
        return lines

    def block(self, x, y, lines, fnt, fill, leading):
        for line in lines:
            self.text((x, y), line, fnt, fill)
            y += leading
        return y

    # -- halftone photo placeholder: dot grid, darker on one side -------
    def halftone(self, box, seed):
        rng = random.Random(seed)
        x0, y0, x1, y1 = box
        self.d.rectangle(box, fill=PHOTO_BG, outline=INK, width=1)
        step = 7
        for gy in range(y0 + 4, y1 - 3, step):
            for gx in range(x0 + 4, x1 - 3, step):
                # darker upper-left, fading to the lower-right
                shade = 1.0 - 0.5 * ((gx - x0) / max(1, x1 - x0)
                                     + (gy - y0) / max(1, y1 - y0)) / 2
                shade += rng.uniform(-0.15, 0.15)
                r = max(0.4, min(2.6, 2.6 * shade))
                self.d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=INK)

    # -- line-art icons ---------------------------------------------------
    def gamepad(self, cx, cy, s=1.0):
        d = self.d
        w, h = int(46 * s), int(30 * s)
        x0, y0 = cx - w // 2, cy - h // 2
        d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=int(10 * s),
                            outline=INK, width=2)
        # d-pad
        px, py = x0 + int(11 * s), y0 + h // 2
        d.line([(px - 5, py), (px + 5, py)], fill=INK, width=2)
        d.line([(px, py - 5), (px, py + 5)], fill=INK, width=2)
        # buttons + sticks
        bx = x0 + w - int(12 * s)
        d.ellipse([bx - 3, py - 8, bx + 3, py - 2], outline=INK, width=2)
        d.ellipse([bx - 3, py + 2, bx + 3, py + 8], outline=INK, width=2)
        d.ellipse([x0 + w // 2 - 4, y0 + h - 7, x0 + w // 2 + 2, y0 + h - 1],
                  outline=INK, width=2)

    def probe(self, cx, cy, s=1.0):
        d = self.d
        # dish + bus + boom + antenna (Voyager 1, side view)
        d.ellipse([cx - int(26 * s), cy - int(12 * s),
                   cx - int(2 * s), cy + int(12 * s)], outline=INK, width=2)
        d.rectangle([cx - int(2 * s), cy - int(7 * s),
                     cx + int(12 * s), cy + int(7 * s)], outline=INK, width=2)
        d.line([(cx + int(12 * s), cy), (cx + int(30 * s), cy - int(8 * s))],
               fill=INK, width=2)
        d.line([(cx + int(12 * s), cy - int(7 * s)),
                (cx + int(26 * s), cy - int(16 * s))], fill=INK, width=2)
        d.ellipse([cx + int(24 * s), cy - int(19 * s),
                   cx + int(28 * s), cy - int(15 * s)], outline=INK, width=2)

    def sun(self, cx, cy, r=7):
        d = self.d
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
        for k in range(8):
            import math
            a = k * 3.14159 / 4
            x1 = cx + int((r + 2) * math.cos(a))
            y1 = cy + int((r + 2) * math.sin(a))
            x2 = cx + int((r + 6) * math.cos(a))
            y2 = cy + int((r + 6) * math.sin(a))
            d.line([(x1, y1), (x2, y2)], fill=INK, width=2)

    # -- finish: ink-bleed blur, paper grain, vignette --------------------
    def finish(self):
        blurred = self.ov.filter(ImageFilter.GaussianBlur(0.5))
        self.img.paste(Image.alpha_composite(
            self.img.convert("RGBA"), blurred).convert("RGB"), (0, 0))
        # paper fibre: grey noise tile, Multiply at 15%
        rng = random.Random(20261119)
        tile = Image.new("L", (256, 256))
        tile.putdata([rng.randint(225, 255) for _ in range(256 * 256)])
        tile = tile.resize((W, H), Image.BICUBIC).convert("RGB")
        self.img = Image.blend(self.img,
                               ImageChops.multiply(self.img, tile), 0.15)
        # 20px vignette: darkened edges
        mask = Image.new("L", (128, 128), 0)
        md = ImageDraw.Draw(mask)
        md.rectangle([3, 3, 124, 124], fill=255)
        mask = mask.resize((W, H), Image.BICUBIC)
        dark = ImageEnhance.Brightness(self.img).enhance(0.80)
        self.img = Image.composite(self.img, dark, mask)
        # 5% black speckle (ink flecks)
        sp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sp)
        rng2 = random.Random(7)
        for _ in range(900):
            x, y = rng2.randint(0, W - 1), rng2.randint(0, H - 1)
            sd.point((x, y), fill=(0, 0, 0, 13))
        self.img = Image.alpha_composite(
            self.img.convert("RGBA"), sp).convert("RGB")
        return self.img


def draw_crossword(p, x, y, w):
    """Mini 5x5 crossword: PEACE across, PACT down. Fills a dead corner."""
    p.text((x, y), "THE DAILY GRID", font(SANS_B, 16), RED)
    y += 22
    cell = 20
    gx, gy = x, y
    letters = {(0, 0): "P", (1, 0): "E", (2, 0): "A", (3, 0): "C",
               (4, 0): "E", (0, 1): "A", (0, 2): "C", (0, 3): "T"}
    f_let = font(SERIF_B, 13)
    for row in range(5):
        for col in range(5):
            box = [gx + col * cell, gy + row * cell,
                   gx + (col + 1) * cell, gy + (row + 1) * cell]
            p.d.rectangle(box, outline=HAIR, width=1)
            ch = letters.get((col, row))
            if ch:
                tw = p.t.textlength(ch, font=f_let)
                p.text((box[0] + (cell - tw) / 2, box[1] + 3),
                       ch, f_let, INK)
    y = gy + 5 * cell + 6
    f_clue = font(SANS, 12)
    for line in p.wrap("1 Across \u2014 What Shenzhen declared (5).",
                       f_clue, w, limit=2):
        p.text((x, y), line, f_clue, BODY)
        y += 16
    return y


def build(seed=19, out=None):
    p = Page(seed)
    d, t = p.d, p.t
    y = 32

    # ---- eyebrow: left tagline, right date + issue no. + weather -------
    f_eye = font(SANS_B, 18)
    p.text((M, y), "THE WORLD IN ONE IMAGE", f_eye, RED)
    right = "THURSDAY  \u2022  VOL. VII \u2014 No. 324"
    p.text((W - M - 34 - t.textlength(right, font=f_eye), y), right,
           f_eye, INK)
    p.sun(W - M - 12, y + 10, r=7)
    y += 26
    d.line([(M, y), (W - M, y)], fill=INK, width=2)
    y += 10

    # ---- masthead -------------------------------------------------------
    size = 54
    f_mast = font(SERIF_BLACK, size)
    title = "THE WORLD TODAY"
    while t.textlength(title, font=f_mast) > W - 2 * M and size > 40:
        size -= 2
        f_mast = font(SERIF_BLACK, size)
    p.text(((W - t.textlength(title, font=f_mast)) / 2, y), title,
           f_mast, INK)
    y += size + 6

    # ---- dateline + double rule -----------------------------------------
    f_date = font(SERIF, 24)
    date = "Thursday, 19 November 2026"
    p.text(((W - t.textlength(date, font=f_date)) / 2, y), date,
           f_date, INK)
    y += 34
    d.line([(M, y), (W - M, y)], fill=INK, width=4)
    y += 7
    d.line([(M, y), (W - M, y)], fill=INK, width=1)
    y += 12

    # ---- lead story: banner headline across all columns -----------------
    lead = NEWS["lead"]
    f_kick = font(SANS_B, 19)
    p.text((M, y), lead["kicker"], f_kick, RED)
    y += 26
    f_head = font(SERIF_BLACK, 56)
    head_lines = p.wrap(lead["headline"], f_head, W - 2 * M, limit=3)
    y = p.block(M, y, head_lines, f_head, INK, 60)
    y += 14  # clear the descenders of the last headline line
    d.line([(M, y), (W - M, y)], fill=INK, width=3)  # heavy rule
    y += 10
    f_deck = font(SERIF_L, 19)
    y = p.block(M, y, p.wrap(lead["deck"], f_deck, W - 2 * M, limit=2),
                f_deck, BODY, 25)
    y += 8
    d.line([(M, y), (W - M, y)], fill=INK, width=1)  # thin + thick
    y += 4
    d.line([(M, y), (W - M, y)], fill=INK, width=3)
    y += 10
    # lead body with 3-line drop cap
    f_body = font(SERIF_L, 15)
    body_lines = p.wrap(lead["body"], f_body, W - 2 * M - 40, limit=3)
    f_drop = font(SERIF_B, 44)
    first = body_lines[0]
    p.text((M, y - 6), first[0], f_drop, INK)
    drop_w = 32
    indented = [first[1:]] + body_lines[1:]
    y = p.block(M + drop_w, y, indented, f_body, BODY, 20)
    y += 4
    f_src = font(SANS, 14)
    p.text((M, y), lead["sources"], f_src, FAINT)
    y += 24  # clear the sources line's descenders

    # ---- divider, then grid ---------------------------------------------
    d.line([(M, y), (W - M, y)], fill=INK, width=2)
    y += 8
    grid_top = y

    gap = 24
    col_w = (W - 2 * M - 2 * gap) // 3          # 293
    wide_w = col_w * 2 + gap                    # 610
    f_ck = font(SANS_B, 18)
    f_ch = font(SERIF_B, 23)
    f_cb = font(SERIF_L, 14)
    f_cs = font(SANS, 11)
    f_cap = font(SANS_I, 8)

    def story_cell(x, cy, kick, head, body, src, width, photo=None,
                   caption=None):
        """Draw one story; returns its height. photo=(w,h,seed) optional."""
        p.text((x, cy), kick, f_ck, RED)
        hy = cy + 24
        tx, tw = x, width
        if photo:
            pw, ph, pseed = photo
            p.halftone((x + width - pw, hy, x + width, hy + ph), pseed)
            if caption:
                p.text((x + width - pw, hy + ph + 4), caption, f_cap, FAINT)
            tw = width - pw - 14
        y2 = p.block(tx, hy, p.wrap(head, f_ch, tw, limit=3), f_ch, INK, 28)
        y2 = p.block(tx, y2 + 6,
                     p.wrap(body, f_cb, tw, limit=3), f_cb, BODY, 19)
        p.text((tx, y2 + 4), src.upper(), f_cs, FAINT)
        return max(y2 + 14, hy + (photo[1] + 14 if photo else 0)) - cy

    # Row A: Myanmar spans 2 cols (photo right) + Gulf
    s = NEWS["stories"]
    a0 = story_cell(M, grid_top, *s[0], wide_w, photo=(200, 88, 11),
                    caption="The court delivers its verdict. (Illustration)")
    a1 = story_cell(M + wide_w + gap, grid_top, *s[1], col_w)
    row_a = max(a0, a1)
    y = grid_top + row_a + 8
    # Row B: Riyadh / Ukraine / Bangladesh
    b0 = story_cell(M, y, *s[2], col_w)
    b1 = story_cell(M + col_w + gap, y, *s[3], col_w)
    b2 = story_cell(M + 2 * (col_w + gap), y, *s[4], col_w)
    row_b = max(b0, b1, b2)
    y = y + row_b + 8
    # Row C: GTA VI spans 2 cols (halftone + gamepad badge) + crossword
    gx = M + wide_w + gap
    cross_bottom = draw_crossword(p, gx, y, col_w)
    c0 = story_cell(M, y, *s[5], wide_w, photo=(200, 88, 23),
                    caption="GTA VI \u2014 out now. (Illustration)")
    # gamepad badge on the photo's lower-right corner
    bx, by = M + wide_w - 30, y + 24 + 88 - 18
    d.ellipse([bx - 26, by - 18, bx + 26, by + 18], fill=(244, 241, 234),
              outline=INK, width=1)
    p.gamepad(bx, by, s=0.72)
    row_c = max(c0, cross_bottom - y)
    grid_bottom = y + row_c
    assert grid_bottom < 960, grid_bottom

    # column rules: 1px #D0C8B8 between columns, per row band.
    # Wide rows (A, C) have a single rule at the wide/narrow boundary.
    bands = ((grid_top, grid_top + row_a, [M + wide_w + gap // 2]),
             (grid_top + row_a + 8, grid_top + row_a + 8 + row_b,
              [M + col_w + gap // 2, M + 2 * col_w + gap + gap // 2]),
             (grid_top + row_a + 8 + row_b + 8, grid_bottom,
              [M + wide_w + gap // 2]))
    for (top, bot, xs) in bands:
        for x in xs:
            d.line([(x, top + 4), (x, bot - 4)], fill=HAIR, width=1)

    # ---- footer: Voyager 1 + probe line-art ------------------------------
    fy = grid_bottom + 4
    d.line([(M, fy), (W - M, fy)], fill=INK, width=2)
    f_foot = font(SANS, 15)
    foot_lines = p.wrap(NEWS["footer"], f_foot, W - 2 * M - 80, limit=2)
    bottom = fy + 6 + len(foot_lines) * 20
    assert bottom <= 1020, bottom
    p.block(M, fy + 6, foot_lines, f_foot, FAINT, 20)
    p.probe(W - M - 32, fy + 18, s=1.0)

    img = p.finish()
    if out:
        img.save(out, "PNG", optimize=True)
        print("wrote", out, "grid_top", grid_top, "rows", row_a, row_b,
              row_c, "grid_bottom", grid_bottom, "bottom", bottom)
    return img


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 19
    build(seed=seed, out=out)
