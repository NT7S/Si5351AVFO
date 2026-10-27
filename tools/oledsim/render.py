#!/usr/bin/env python3
"""Scale SH1106 PBM frames to 4x PNGs and build a before/after contact sheet.

Reads the 5x7 font out of sh1106.cpp so captions match the panel, and checks
that every menu row scrolls into view.
"""
import os
import re
import struct
import sys
import zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
FW = os.path.join(ROOT, "..", "..", "firmware", "Si5351AVFO")
SCALE = 4

# OLED white on black, the usual 1.3" module.
ON = (232, 244, 255)
OFF = (8, 10, 12)
LABEL = (220, 224, 230)
LABEL_BG = (28, 32, 38)


def parse_font():
    src = open(os.path.join(FW, "sh1106.cpp")).read()
    body = src.split("font5x7[] = {", 1)[1].split("};", 1)[0]
    nums = []
    for tok in body.replace("\n", " ").split(","):
        tok = tok.strip()
        if not tok:
            continue
        nums.append(int(tok, 0))
    font = {}
    for i in range(len(nums) // 5):
        font[chr(0x20 + i)] = nums[i * 5 : i * 5 + 5]
    return font


FONT = parse_font()

ITEMS = [
    "OUTPUT MODE", "CLK0 OUTPUT", "CLK1 OUTPUT", "CLK2 OUTPUT", "IF FREQ",
    "LO INJECTION", "IQ ORDER", "TUNING LIMIT", "CLK0 DRIVE", "CLK1 DRIVE",
    "CLK2 DRIVE", "CLK0 FILT OVR", "CLK1 FILT OVR", "CLK2 FILT OVR",
    "MEM STORE", "MEM RECALL", "MEM CLEAR", "CALIBRATE PPB", "RESET SETTINGS",
    "FACTORY RESET", "ABOUT",
]


def load_pbm(path):
    lines = open(path).read().splitlines()
    if lines[0] != "P1":
        raise SystemExit("not a P1 bitmap: " + path)
    w, h = map(int, lines[1].split())
    toks = []
    for ln in lines[2:]:
        toks.extend(ln.split())
    rows = []
    for y in range(h):
        rows.append([1 if toks[y * w + x] == "1" else 0 for x in range(w)])
    return rows


def page_bytes(rows, page):
    cols = []
    for x in range(len(rows[0])):
        b = 0
        for bit in range(8):
            if rows[page * 8 + bit][x]:
                b |= 1 << bit
        cols.append(b)
    return cols


def match_glyph(glyph):
    """Return (char, inverted). Accepts the old full-byte invert and the
    current bar, which clears the bottom pixel (~glyph & 0x7F)."""
    for cand, g in FONT.items():
        if list(g) == glyph:
            return cand, False
    flipped = [((b ^ 0xFF) & 0x7F) for b in glyph]
    for cand, g in FONT.items():
        if list(g) == flipped:
            return cand, True
    return ("?" if any(glyph) else " "), None


def decode_page(rows, page):
    cols = page_bytes(rows, page)
    if not any(cols):
        return "", False
    text = []
    inverted = 0
    normal = 0
    x = 0
    while x + 5 <= len(cols):
        ch, inv = match_glyph(cols[x : x + 5])
        if inv:
            inverted += 1
        elif inv is False:
            normal += 1
        text.append(ch)
        x += 6
    s = "".join(text).rstrip()
    return s, inverted > normal and inverted > 0


def write_png(path, rgb, w, h):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + rgb[y * w * 3 : (y + 1) * w * 3] for y in range(h))
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(png)


def scale_rows(rows, n=SCALE, on=ON, off=OFF):
    h = len(rows)
    w = len(rows[0])
    out_w, out_h = w * n, h * n
    rgb = bytearray(out_w * out_h * 3)
    for y in range(h):
        for x in range(w):
            color = on if rows[y][x] else off
            for dy in range(n):
                for dx in range(n):
                    i = ((y * n + dy) * out_w + (x * n + dx)) * 3
                    rgb[i : i + 3] = bytes(color)
    return rgb, out_w, out_h


def draw_text(rgb, w, h, x, y, text, color, n=2):
    for ch in text.upper():
        glyph = FONT.get(ch, FONT.get(" ", [0] * 5))
        for col, bits in enumerate(glyph):
            for bit in range(7):
                if bits & (1 << bit):
                    for dy in range(n):
                        for dx in range(n):
                            px, py = x + col * n + dx, y + bit * n + dy
                            if 0 <= px < w and 0 <= py < h:
                                i = (py * w + px) * 3
                                rgb[i : i + 3] = bytes(color)
        x += 6 * n
    return x


def rightmost_lit(rows):
    w = len(rows[0])
    last = -1
    for y in rows:
        for x in range(w - 1, -1, -1):
            if y[x]:
                last = max(last, x)
                break
    return last


def list_rows(rows):
    """Non-empty pages between the title (0) and the key labels (7)."""
    found = []
    for page in range(1, 7):
        text, inv = decode_page(rows, page)
        if text.strip():
            found.append((page, text.strip(), inv))
    return found


def glyph_bits(rows, x, y, inv):
    cols = []
    for k in range(5):
        b = 0
        for bit in range(7):
            on = rows[y + bit][x + k]
            if inv:
                on = 0 if on else 1
            if on:
                b |= 1 << bit
        cols.append(b)
    for cand, g in FONT.items():
        if list(g) == cols:
            return cand
    return None


def pitched_rows(rows, y0=11, dy=10, n=4):
    """Menu rows drawn at a 10 px pitch (see MENU_Y0 / MENU_DY in ui.cpp)."""
    found = []
    for r in range(n):
        y = y0 + r * dy
        if y + 6 >= len(rows):
            break
        inv = rows[y][0] == 1
        chars = []
        for i in range(18):
            ch = glyph_bits(rows, i * 6, y, inv)
            if ch is None:
                chars.append("?")
            else:
                chars.append(ch)
        text = "".join(chars).strip()
        if text:
            found.append((y, text, inv))
    return found


def menu_window(rows):
    """Page-packed menus (older firmware) or the pitched menu."""
    paged = list_rows(rows)
    if paged and all(any(text.endswith(it) for it in ITEMS) for _, text, _ in paged):
        return paged
    return pitched_rows(rows)


def check_scroll(raw_dir):
    """Encoder steps 0..20 must window all 21 items the way ui.cpp does."""
    frames = []
    for i in range(21):
        name = "menu_top" if i == 0 else ("menu_pos_%02d" % i)
        # menu_pos_20 is also copied to menu_bottom; either file is fine.
        path = os.path.join(raw_dir, name + ".pbm")
        if not os.path.exists(path) and i == 20:
            path = os.path.join(raw_dir, "menu_bottom.pbm")
        frames.append(load_pbm(path))
    rows0 = menu_window(frames[0])
    menu_rows = len(rows0)
    if menu_rows < 2 or menu_rows > 6:
        raise SystemExit("unexpected menu row count %d" % menu_rows)
    top = 0
    for sel, rows in enumerate(frames):
        if sel < top:
            top = sel
        if sel >= top + menu_rows:
            top = sel - menu_rows + 1
        got = menu_window(rows)
        if len(got) != menu_rows:
            raise SystemExit("sel %d shows %d rows, expected %d" % (sel, len(got), menu_rows))
        for i, (page, text, inv) in enumerate(got):
            label = ITEMS[top + i]
            if not text.endswith(label):
                raise SystemExit("sel %d row %d %r, expected %r" % (sel, i, text, label))
            if inv != (top + i == sel):
                raise SystemExit("sel %d row %d inverted=%s" % (sel, i, inv))
    # Page down / page up use the same window size.
    down = menu_window(load_pbm(os.path.join(raw_dir, "menu_page_down.pbm")))
    if not any(inv and text.endswith(ITEMS[menu_rows]) for _, text, inv in down):
        raise SystemExit("page down did not land on item %d" % menu_rows)
    up = menu_window(load_pbm(os.path.join(raw_dir, "menu_page_up.pbm")))
    if not any(inv and text.endswith(ITEMS[0]) for _, text, inv in up):
        raise SystemExit("page up did not return to the first item")
    print("scroll ok: %d rows, all %d items" % (menu_rows, len(ITEMS)))
    return menu_rows


def glyph_at(rows, x, y0):
    cols = []
    for col in range(5):
        b = 0
        for bit in range(7):
            if rows[y0 + bit][x + col]:
                b |= 1 << bit
        cols.append(b)
    for cand, g in FONT.items():
        if list(g) == cols:
            return cand
    return None


def read_text_at(rows, x, y0, nchars):
    out = []
    for i in range(nchars):
        ch = glyph_at(rows, x + i * 6, y0)
        if ch is None:
            return None
        out.append(ch)
    return "".join(out)


def is_pitched_menu(rows):
    """True for the 10 px menu. Page-packed frames still decode as items."""
    paged = list_rows(rows)
    if paged and all(any(text.endswith(it) for it in ITEMS) for _, text, _ in paged):
        return False
    return bool(pitched_rows(rows))


def row_full(rows, y):
    return 0 <= y < len(rows) and all(rows[y])


def row_dark(rows, y):
    return y < 0 or y >= len(rows) or not any(rows[y])


def check_highlight(raw_dir):
    """9 px selection bar on the pitched menu: 1 px pad above and below the
    7 px glyph, 10 px row pitch, no contact with the next row or the labels,
    and every glyph still readable inside the panel."""
    sample = os.path.join(raw_dir, "menu_top.pbm")
    if not os.path.exists(sample) or not is_pitched_menu(load_pbm(sample)):
        print("highlight pad: skipped (page-packed menu)")
        return
    fails = 0
    pitch = [11, 21, 31, 41]
    for name in sorted(os.listdir(raw_dir)):
        if not name.endswith(".pbm"):
            continue
        if not (name.startswith("menu_") or name.startswith("save_")):
            continue
        rows = load_pbm(os.path.join(raw_dir, name))
        if not is_pitched_menu(rows):
            print(name, "is not a pitched menu")
            fails += 1
            continue
        got = pitched_rows(rows)
        if [y for y, _, _ in got] != pitch:
            print(name, "pitch", [y for y, _, _ in got])
            fails += 1
        for y in range(7, 10):
            if not row_dark(rows, y):
                print(name, "row", y, "lit under the title")
                fails += 1
        for y in range(49, 56):
            if not row_dark(rows, y):
                print(name, "row", y, "lit above the key labels")
                fails += 1
        for y, text, inv in got:
            if y < 0 or y + 6 > 63:
                print(name, "glyph clipped at", y)
                fails += 1
            if "?" in text:
                print(name, "unreadable glyph in", text)
                fails += 1
            if inv:
                # Pad rows are solid. The rows just outside the 9 px bar are dark,
                # which is the gap to the title, the next row, or the labels.
                if not row_full(rows, y - 1) or not row_full(rows, y + 7):
                    print(name, "bar pad missing around", text, "at", y)
                    fails += 1
                if not row_dark(rows, y - 2) or not row_dark(rows, y + 8):
                    print(name, "bar touches a neighbour", text, "at", y)
                    fails += 1
            elif not row_dark(rows, y - 1) or not row_dark(rows, y + 7):
                print(name, "unselected row has a bar", text)
                fails += 1
    if fails:
        raise SystemExit("%d highlight checks failed" % fails)
    print("highlight ok: 9 px bar, 10 px pitch, labels clear")


def check_messages(raw_dir):
    """Title-line confirmations and CANCEL must stay inside 128 columns."""
    fails = 0
    for name in sorted(os.listdir(raw_dir)):
        if not name.endswith(".pbm"):
            continue
        rows = load_pbm(os.path.join(raw_dir, name))
        last = rightmost_lit(rows)
        if last > 127:
            print("OVERFLOW", name, last)
            fails += 1
        title, _ = decode_page(rows, 0)
        if len(title.strip()) > 21:
            print("TITLE TOO LONG", name, title)
            fails += 1
    edit = load_pbm(os.path.join(raw_dir, "edit_choice.pbm"))
    # LABEL_X2 is 110; CANCEL is 6 chars, so the cell starts at 110 - 18 = 92
    # and ends at column 128. The last column is the glyph spacer (unlit).
    word = read_text_at(edit, 92, 56, 6)
    if word != "CANCEL":
        print("CANCEL missing at column 92:", word)
        fails += 1
    last = rightmost_lit([edit[y] for y in range(56, 64)])
    if last != 126:
        print("CANCEL extent changed: last lit column", last)
        fails += 1
    if fails:
        raise SystemExit("%d message/width checks failed" % fails)
    print("width ok")


PAIRS = [
    ("main_normal", "Main, direct"),
    ("main_superhet", "Main, superhet"),
    ("menu_top", "Menu, top"),
    ("menu_pos_10", "Menu, middle"),
    ("menu_bottom", "Menu, bottom"),
    ("save_mode", "Save: output mode"),
    ("save_clk", "Save: CLK0"),
    ("save_drive", "Save: CLK0 drive"),
    ("save_limit", "Save: tuning limit"),
    ("save_filter", "Save: CLK0 filter"),
    ("save_if", "Save: IF frequency"),
    ("save_inject", "Save: LO injection"),
    ("save_memory", "Save: memory store"),
    ("save_cal", "Save: calibration"),
]


def png_of(rows):
    return scale_rows(rows)


def contact(before_dir, after_dir, out_path):
    tiles = []
    for name, caption in PAIRS:
        b = load_pbm(os.path.join(before_dir, name + ".pbm"))
        a = load_pbm(os.path.join(after_dir, name + ".pbm"))
        tiles.append((caption, png_of(b), png_of(a)))
    img_w = 128 * SCALE
    img_h = 64 * SCALE
    label_w = 210
    pad = 12
    head = 28
    row_h = head + img_h + pad
    sheet_w = label_w + pad + img_w + pad + img_w + pad
    sheet_h = pad + len(tiles) * row_h + 8
    rgb = bytearray([18, 20, 24]) * (sheet_w * sheet_h)
    # column headings
    for caption, (brgb, bw, bh), (argb, aw, ah) in tiles:
        pass
    for i, (caption, (brgb, bw, bh), (argb, aw, ah)) in enumerate(tiles):
        y0 = pad + i * row_h
        draw_text(rgb, sheet_w, sheet_h, 8, y0 + 4, caption, LABEL, 2)
        draw_text(rgb, sheet_w, sheet_h, label_w + pad, y0 + 4, "Before", LABEL, 2)
        draw_text(rgb, sheet_w, sheet_h, label_w + pad + img_w + pad, y0 + 4, "After", LABEL, 2)
        by = y0 + head
        for src, x0 in ((brgb, label_w + pad), (argb, label_w + pad + img_w + pad)):
            for y in range(img_h):
                dst = ((by + y) * sheet_w + x0) * 3
                src_i = y * img_w * 3
                rgb[dst : dst + img_w * 3] = src[src_i : src_i + img_w * 3]
    write_png(out_path, rgb, sheet_w, sheet_h)
    print("wrote", out_path, sheet_w, sheet_h)


def export_dir(raw_dir, png_dir):
    os.makedirs(png_dir, exist_ok=True)
    names = [n for n, _ in PAIRS]
    for name in names:
        rows = load_pbm(os.path.join(raw_dir, name + ".pbm"))
        rgb, w, h = scale_rows(rows)
        write_png(os.path.join(png_dir, name + ".png"), rgb, w, h)
    print("exported", png_dir)


def main():
    if len(sys.argv) < 3:
        print("usage: render.py <raw-dir> <png-dir> [<after-raw> <contact.png>]")
        return 2
    raw = sys.argv[1]
    png = sys.argv[2]
    check_scroll(raw)
    check_messages(raw)
    check_highlight(raw)
    export_dir(raw, png)
    if len(sys.argv) >= 5:
        check_scroll(sys.argv[3])
        check_messages(sys.argv[3])
        check_highlight(sys.argv[3])
        contact(raw, sys.argv[3], sys.argv[4])
    return 0


if __name__ == "__main__":
    sys.exit(main())
