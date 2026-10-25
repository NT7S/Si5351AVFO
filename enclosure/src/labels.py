"""Debossed panel graphics for the Si5351A VFO front shell, styled after
etherkit/EtherKeyerMini mech/EtherKeyerMiniCaseBottomNew.FCStd (FiraCode Bold,
logo left of a stacked product name, short control labels next to each control).
EKM embosses 1.0 mm on an upright-printed wall; this panel prints face-down, so
everything is DEBOSSED (cut into the outer face) instead."""
import json, os
import cadquery as cq
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "fonts", "Barlow-Bold.ttf")   # main panel face (SIL OFL, see ../fonts/OFL.txt)
FONT_CLK = os.path.join(HERE, "..", "fonts", "BarlowSemiCondensed-Bold.ttf")  # condensed face for the tight CLK0/1/2 row only
TEXT_DEPTH = 0.5          # deboss depth into the 2.0 mm panel (overridden in inlay mode)
INLAY_DEPTH = 0.60        # inlay mode: 0.20 first layer + 2 x 0.20 (rev2 adhesion)
CAP_NAME   = 5.0          # EKM "EtherKeyer Mini" Size 5
CAP_LABEL  = 4.0          # EKM "Speed"/"PDL"/"KEY" Size 4  (FreeCAD Size ~ cap height) -> TUNE, USB
CAP_ROW    = 3.2          # 4-char labels on the 12.7 mm button / 13 mm SMA pitch (4.0 would touch); keep >= 3.0
LOGO_H     = 14.0         # logo spans both name lines, like EKM (19.6 mm there, spanning 2 rows)

PRODUCT_NAME = ["Si5351A", "VFO"]        # stacked lines; edit freely
# button labels: list of lines (top first); a single line sits on the top line so rows align
BTN_LABELS = {}   # buttons are display soft keys; no fixed labels (was BAND UP / BAND DOWN / MENU)
ENC_LABEL  = [("TUNE/", 4.0), ("STEP", 4.0)]   # (text, cap height[, font name]) lines over the encoder, each ink-centred on the shaft
CAP_BTN    = 3.0          # two-line button labels: 4-char words at 12.7 mm pitch -> ~2.6 mm gap between neighbours
LINE_GAP   = 1.4          # clear gap between stacked lines
SMA_LABELS = ["CLK0", "CLK1", "CLK2"]
USB_LABEL  = "USB"        # set to None to omit

# placements in drawing coords (x right, yd down), all on the panel outer face
BTN_X   = {"SW2": 15.0, "SW3": 27.7, "SW4": 40.4}; BTN_LABEL_YD = 51.0   # centre of TOP line above buttons (EKM: digits above holes)
ENC_XY  = (89.0, 30.6)   # x = encoder shaft centre (ENCODER in vfo_case.py); yd = centre of TOP line. Lowest ink ~38.0, i.e. >=1.5 mm outside a 20 mm knob (edge at yd 40.0)
SMA_X   = [58.0, 71.0, 84.0]; TOP_LABEL_YD = 4.5                        # front panel, top edge, over each SMA
USB_XY  = (16.0, 4.5)
LOGO_XY = (51.0, 13.0)            # top-left corner of logo bbox
NAME_X, NAME_YD = 61.0, (16.0, 24.5)   # left edge, centre of each line

_k = {}
def _font_k(font=None):
    font = font or FONT
    if font not in _k:
        bb = cq.Workplane("XY").text("H", 10.0, 1.0, fontPath=font).val().BoundingBox()
        _k[font] = 10.0 / bb.ylen
    return _k[font]

def _text(s, cap, x, yd, z, halign="center", font=None):
    font = font or FONT
    t = cq.Workplane("XY").text(s, cap*_font_k(font), TEXT_DEPTH + 0.5, fontPath=font,
                                halign=halign, valign="bottom")
    bb = t.val().BoundingBox()
    # place so cap height is centred on yd (ignore descenders: none in our labels)
    return t.translate((x, -yd - cap/2, z - TEXT_DEPTH))

def _logo(x0, yd0, h, z):
    g = shape(json.load(open(os.path.join(HERE, "etherkit_logo_ekm.json")))).simplify(0.01)
    s = h / (g.bounds[3] - g.bounds[1])
    def wire(ring):
        pts = [cq.Vector(x0 + px*s, -yd0 - h + py*s, 0) for px, py in list(ring.coords)[:-1]]
        return cq.Wire.makePolygon(pts, close=True)
    face = cq.Face.makeFromWires(wire(g.exterior), [wire(i) for i in g.interiors])
    sol = cq.Solid.extrudeLinear(face, cq.Vector(0, 0, TEXT_DEPTH + 0.5))
    return cq.Workplane().add(sol.translate(cq.Vector(0, 0, z - TEXT_DEPTH)))

def graphics(panel_out, depth=None):
    global TEXT_DEPTH
    if depth is not None: TEXT_DEPTH = depth
    z = panel_out
    cut = _logo(*LOGO_XY, LOGO_H, z)
    for line, yd in zip(PRODUCT_NAME, NAME_YD):
        cut = cut.union(_text(line, CAP_NAME, NAME_X, yd, z, halign="left"))
    for k, v in BTN_LABELS.items():
        for i, line in enumerate([v] if isinstance(v, str) else v):
            cut = cut.union(_text(line, CAP_BTN, BTN_X[k], BTN_LABEL_YD + i*(CAP_BTN + LINE_GAP), z))
    lines = [(ENC_LABEL, CAP_LABEL)] if isinstance(ENC_LABEL, str) else ENC_LABEL
    yd = ENC_XY[1]
    for i, ln in enumerate(lines):
        t, cap = ln[0], ln[1]; f = globals()[ln[2]] if len(ln) > 2 else None
        if i: yd += lines[i-1][1]/2 + LINE_GAP + cap/2
        g = _text(t, cap, ENC_XY[0], yd, z, font=f)
        b = g.val().BoundingBox()
        cut = cut.union(g.translate((ENC_XY[0] - (b.xmin + b.xmax)/2, 0, 0)))   # centre the INK, not the advance
    for x, v in zip(SMA_X, SMA_LABELS):
        cut = cut.union(_text(v, CAP_ROW, x, TOP_LABEL_YD, z, font=FONT_CLK))
    if USB_LABEL:
        cut = cut.union(_text(USB_LABEL, CAP_LABEL, *USB_XY, z))
    return cut
