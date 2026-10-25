#!/usr/bin/env python3
"""
Parametric two-piece 3D-printable enclosure for the Etherkit Si5351A VFO board
(NT7S/Si5351AVFO, PR #3 @ 51cd370, docs/mechanical/Si5351AVFO_board.step).

Frame = the board STEP frame: X right (0..100), Y = -y_drawing (top edge at Y=0,
board at Y -65..0), Z up with PCB bottom at Z=0 and PCB top at Z=1.6.
Drawing coordinates (x, y_down) from Si5351AVFO_outline.pdf are converted with P().

Parts: front shell (panel + walls + bosses), back cover (plate + standoffs + tabs).
Screws: 4x M3x12 countersunk (ISO 10642 / DIN 7991) from the back, through
cover standoff + plated PCB hole into the front boss (heat-set insert or self-tap).
"""
import os, sys, math
import cadquery as cq

# ------------------------------------------------------------------ parameters
CLR        = 0.4    # board edge -> wall inner face
WALL       = 2.2    # side wall thickness
PANEL_T    = 2.0    # front panel thickness
PANEL_OUT  = 11.5   # Z of panel outer face (button plunger top is 12.6 -> 1.1 proud)
BOTTOM_GAP = 4.0    # PCB bottom -> back cover inner face (THT pin tails, EC11 legs)
COVER_T    = 2.0    # back cover plate thickness
RIM_GAP    = 0.1    # shell rim stops short of cover so screws clamp the PCB
FIT        = 0.4    # general clearance around parts through openings
BOSS_OD    = 6.8    # front boss / rear standoff OD (PCB pad is 6.4)
FASTENER   = "insert"   # "insert" (M3 x 5.7 heat-set, hole 4.0) or "selftap" (hole 2.6)
INSERT_D, INSERT_L = 4.0, 6.0
SELFTAP_D, SELFTAP_L = 2.6, 7.5
OLED_PINS  = "trimmed"     # "pocket" = clearance pocket over untrimmed DS1 header pins, "trimmed" = solid panel (pins cut to <= Z 9.1)
USBC_RELIEF = "full"    # "pocket" = 0.8 mm wall in front of receptacle + overmold pocket, "full" = overmold-size opening through the wall
USBC_OVERMOLD = (12.4, 6.6)   # plug overmold W x H (USB Type-C spec recommended max 12.35 x 6.5)
J5_ACCESS  = "pocket"     # "slot" = UPDI header reachable through panel, "pocket" = blind recess
OLED_WIN_MARGIN = 1.0   # window = active area + margin each side
WIN_CHAMFER = 1.0       # 45deg bevel on window outer edge
OLED_STOP_GAP = 0.3     # gap between panel stops and OLED glass / module PCB
BTN_HOLE   = 3.5 + 2*FIT    # KH-6X6X11H plunger dia 3.5
ENC_HOLE   = 7.6            # EC11 M7 bushing (model dia 7.0)
PANEL_GRAPHICS = "inlay"   # "inlay" = flush 2nd-colour inlay (separate solid), True = debossed name, Etherkit logo, control labels (labels.py)
ENC_RING_GAP = 0.2       # ring stops 0.2 above encoder body; nut takes up the gap
OUT        = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ board facts (verified from STEP)
BOARD_W, BOARD_H, BOARD_R, PCB_T = 100.0, 65.0, 3.0, 1.6
HOLES      = [(4, 4), (96, 4), (4, 61), (96, 61)]
OLED_ACTIVE = (12.99, 29.35, 42.41, 44.05)
OLED_GLASS  = (10.5, 27.25, 44.9, 50.25); GLASS_TOP_Z = 6.8   # 5.2 above PCB
OLED_MODULE = (10.0, 22.0, 45.4, 55.5);   MODULE_TOP_Z = 5.3  # module PCB top
HDR_PINS    = (18.81, 22.73, 36.59, 25.27); PIN_TOP_Z = 10.14  # DS1/J5 pin tips
J5_BOX      = (46.03, 8.73, 48.57, 18.89)
BUTTONS     = [(15.0, 61.0), (27.7, 61.0), (40.4, 61.0)]; BTN_BODY_TOP_Z = 5.1
ENCODER     = (89.0, 50.0)
# Alps EC11E18244A5 per datasheet (drawing No.3/No.5): bushing base 4.5 above mounting surface,
# bushing M7x0.75 x 7 long, shaft tip 24.5 above mounting surface, leads 3.5 below mounting surface.
# (The board STEP model is shorter: body top 6.5, bushing 6.5-13.0, shaft tip 20.0 above PCB.)
ENC_BODY_TOP_Z    = PCB_T_ABS = 1.6 + 4.5     # 6.1
ENC_BUSHING_TOP_Z = 1.6 + 4.5 + 7.0           # 13.1
ENC_SHAFT_TOP_Z   = 1.6 + 24.5                # 26.1
ENC_NUT_T, ENC_WASHER_T = 2.0, 0.5            # M7x0.75 nut/washer (not supplied with EC11E)
ENC_THREAD_SPARE  = 0.6                       # extra thread above nut
ENC_RECESS_D      = 16.0                      # outer recess for nut + washer + socket
ENC_MEMBRANE      = 0.2                       # sacrificial bridge layer over the hole (cut out after printing)
USB         = dict(x=16.0, w=8.94, z0=1.6, z1=4.86, plug_w=USBC_OVERMOLD[0], plug_h=USBC_OVERMOLD[1])
SMA_X       = [58.0, 71.0, 84.0]; SMA_FLANGE = 6.4; SMA_FLANGE_DEPTH = 1.6; SMA_BARREL = 6.2; SMA_AXIS_Z = 1.6

def P(x, yd, z=0.0):
    return (x, -yd, z)

# derived
IN_W, IN_H = BOARD_W + 2*CLR, BOARD_H + 2*CLR
OUT_W, OUT_H = IN_W + 2*WALL, IN_H + 2*WALL
R_IN, R_OUT = BOARD_R + CLR, BOARD_R + CLR + WALL
CX, CY = BOARD_W/2, -BOARD_H/2
Z_PIN = PANEL_OUT - PANEL_T          # panel inner face
Z_RIM = -BOTTOM_GAP + RIM_GAP
Z_COVER_IN, Z_COVER_OUT = -BOTTOM_GAP, -BOTTOM_GAP - COVER_T
WALL_Y0, WALL_Y1 = CLR, CLR + WALL   # top (connector) wall, STEP Y

def rbox(w, h, r, z0, z1, cx=CX, cy=CY):
    return (cq.Workplane("XY").workplane(offset=z0).center(cx, cy)
            .rect(w, h).extrude(z1 - z0).edges("|Z").fillet(r))

def box(x0, y0, x1, y1, z0, z1):
    """axis box in STEP coords"""
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0))

def dbox(xa, yda, xb, ydb, z0, z1):
    """axis box from drawing-coordinate rectangle"""
    return box(xa, -ydb, xb, -yda, z0, z1)

def cyl(x, yd, d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(x, -yd).circle(d/2).extrude(z1 - z0)

def cone(x, yd, d0, z0, d1, z1):
    return cq.Workplane().add(cq.Solid.makeCone(d0/2, d1/2, z1 - z0, cq.Vector(x, -yd, z0)))

def u_notch(xc, w, ztop, r, y0, y1, zbot):
    """U-shaped notch through the top wall, open toward the rim (zbot), rounded top corners"""
    b = box(xc - w/2, y0, xc + w/2, y1, zbot, ztop)
    return b.edges("|Y").edges(">Z").fillet(r) if r > 0 else b

# ------------------------------------------------------------------ front shell
def front_shell():
    s = rbox(OUT_W, OUT_H, R_OUT, Z_RIM, PANEL_OUT)
    s = s.cut(rbox(IN_W, IN_H, R_IN, Z_RIM - 1, Z_PIN))
    hole_d, hole_l = (INSERT_D, INSERT_L) if FASTENER == "insert" else (SELFTAP_D, SELFTAP_L)
    for x, yd in HOLES:   # bosses clamp the PCB top around the plated holes
        s = s.union(cyl(x, yd, BOSS_OD, PCB_T, Z_PIN + 0.01))
        s = s.cut(cyl(x, yd, hole_d, PCB_T - 0.1, PCB_T + hole_l))
    # OLED: glass frame lip (stops just above glass, outside the active window)
    wx0, wy0, wx1, wy1 = (OLED_ACTIVE[0]-OLED_WIN_MARGIN, OLED_ACTIVE[1]-OLED_WIN_MARGIN,
                          OLED_ACTIVE[2]+OLED_WIN_MARGIN, OLED_ACTIVE[3]+OLED_WIN_MARGIN)
    g = OLED_GLASS; ins = 0.3
    frame = dbox(g[0]+ins, g[1]+ins, g[2]-ins, g[3]-ins, GLASS_TOP_Z + OLED_STOP_GAP, Z_PIN + 0.01)
    s = s.union(frame)
    # OLED: four corner stop posts over the module PCB corners (clear of header pins and FPC)
    m = OLED_MODULE
    for (xa, xb) in ((m[0]+0.5, m[0]+3.5), (m[2]-3.5, m[2]-0.5)):
        for (ya, yb) in ((m[1]+0.5, m[1]+3.5), (m[3]-3.5, m[3]-0.5)):
            s = s.union(dbox(xa, ya, xb, yb, MODULE_TOP_Z + OLED_STOP_GAP, Z_PIN + 0.01))
    # window with 45deg bevel on the outside
    s = s.cut(dbox(wx0, wy0, wx1, wy1, GLASS_TOP_Z + 0.1, PANEL_OUT + 1))
    c = WIN_CHAMFER
    bevel = (cq.Workplane("XY").workplane(offset=PANEL_OUT - c).center((wx0+wx1)/2, -(wy0+wy1)/2)
             .rect(wx1-wx0, wy1-wy0).workplane(offset=c + 0.01).rect(wx1-wx0+2*c+0.02, wy1-wy0+2*c+0.02).loft())
    s = s.cut(bevel)
    # header pin pocket (DS1 pin tips reach Z 10.14)
    h = HDR_PINS
    if OLED_PINS == "pocket":
        s = s.cut(dbox(h[0]-0.4, h[1]-0.4, h[2]+0.4, h[3]+0.4, Z_PIN - 1, PIN_TOP_Z + 0.45))
    # J5 UPDI header
    j = J5_BOX
    jz1 = PANEL_OUT + 1 if J5_ACCESS == "slot" else PIN_TOP_Z + 0.45
    s = s.cut(dbox(j[0]-0.5, j[1]-0.5, j[2]+0.5, j[3]+0.5, Z_PIN - 1, jz1))
    # buttons: guide sleeves + plunger holes with 0.5 chamfer
    for x, yd in BUTTONS:
        s = s.union(cyl(x, yd, BTN_HOLE + 2.4, BTN_BODY_TOP_Z + 0.5, Z_PIN + 0.01))
        s = s.cut(cyl(x, yd, BTN_HOLE, BTN_BODY_TOP_Z, PANEL_OUT + 1))
        s = s.cut(cone(x, yd, BTN_HOLE, PANEL_OUT - 0.5, BTN_HOLE + 1.02, PANEL_OUT + 0.01))
    # encoder: spacer ring seated on encoder body (nut clamps panel to body), bushing hole
    ex, ey = ENCODER
    z_floor = ENC_BUSHING_TOP_Z - ENC_NUT_T - ENC_WASHER_T - ENC_THREAD_SPARE
    s = s.union(cyl(ex, ey, 11.0, ENC_BODY_TOP_Z + ENC_RING_GAP, Z_PIN + 0.01))
    s = s.union(cyl(ex, ey, ENC_RECESS_D + 3.0, Z_PIN - 1.0, Z_PIN + 0.01))     # stiffening disk under recess
    if z_floor < PANEL_OUT:
        s = s.cut(cyl(ex, ey, ENC_RECESS_D, z_floor, PANEL_OUT + 1))
    s = s.cut(cyl(ex, ey, ENC_HOLE, ENC_BODY_TOP_Z - 1, min(z_floor, PANEL_OUT) - ENC_MEMBRANE))
    # top-edge wall openings (U-notches open toward rim -> supportless)
    zb = Z_RIM - 1
    u = USB
    s = s.cut(u_notch(u["x"], u["w"] + 2*FIT, u["z1"] + FIT, 0.8, WALL_Y0 - 0.3, WALL_Y1 + 0.1, zb))
    zc = (u["z0"] + u["z1"]) / 2
    plug = dict(y0=WALL_Y0 + (0.8 if USBC_RELIEF == "pocket" else -0.3))       # leave 0.8 mm wall in front of receptacle, rest is plug-overmold pocket
    s = s.cut(u_notch(u["x"], u["plug_w"] + 2*FIT, zc + u["plug_h"]/2 + FIT, 1.5, plug["y0"], WALL_Y1 + 0.1, zb))
    for x in SMA_X:
        fl = SMA_FLANGE + 2*FIT
        s = s.cut(u_notch(x, fl, SMA_AXIS_Z + SMA_FLANGE/2 + FIT, 0.0, WALL_Y0 - 0.3, SMA_FLANGE_DEPTH + 0.3, zb))
        rb = SMA_BARREL/2 + FIT
        s = s.cut(box(x - rb, SMA_FLANGE_DEPTH + 0.2, x + rb, WALL_Y1 + 0.1, zb, SMA_AXIS_Z))
        s = s.cut(cq.Workplane("XZ").workplane(offset=-(SMA_FLANGE_DEPTH + 0.2)).center(x, SMA_AXIS_Z)
                  .circle(rb).extrude(-(WALL_Y1 - SMA_FLANGE_DEPTH + 0.2)))
    if PANEL_GRAPHICS == "inlay":
        return s.cut(panel_inlay(s))
    if PANEL_GRAPHICS:                     # debossed name/logo/labels, see labels.py
        import labels
        s = s.cut(labels.graphics(PANEL_OUT))
    return s

_inlay = None
INLAY_MIN_STROKE = 0.8   # widen only features narrower than this (0.4 mm nozzle); None = off
THIN_REPORT = {}
def _thicken(g, z, depth, w):
    """2D: P' = P U buffer(thin parts of P); re-extrude flush (z-depth .. z+0.5)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    sec = g.section(z - depth/2)
    polys = []
    for f in sec.faces().vals():
        ring = lambda wr: [(v.x, v.y) for v in wr.sample(max(40, int(wr.Length()/0.05)))[0]] if hasattr(wr, "sample") else None
        def pts(wr):
            e = cq.Wire.assembleEdges(wr.Edges()) if False else wr
            n = max(40, int(wr.Length()/0.05))
            return [(p.x, p.y) for p in [wr.positionAt(i/n) for i in range(n)]]
        polys.append(Polygon(pts(f.outerWire()), [pts(h) for h in f.innerWires()]).buffer(0))
    P = unary_union(polys); r = w/2
    # mitred morphological opening: keeps sharp convex corners, so only genuinely thin strokes show up as "lost"
    M = dict(join_style=2, mitre_limit=10.0)
    O = P.buffer(-r, **M).buffer(r, **M)
    lost = P.difference(O)
    lost = unary_union([q for q in getattr(lost, "geoms", [lost]) if q.area > 0.03 and q.buffer(-0.02).area > 0])
    # grow the real outline (mitred offset, no round caps) only where it is thin
    d = 0.1
    add = P.buffer(d, **M).intersection(lost.buffer(d + 0.15, **M)) if not lost.is_empty else lost
    P2 = P.union(add).buffer(0)
    THIN_REPORT.update(area_thin=round(lost.area, 2), added=round(P2.area - P.area, 2), base_area=round(P.area, 1))
    out = None
    for q in getattr(P2, "geoms", [P2]):
        q = q.simplify(0.005)
        mk = lambda c: cq.Wire.makePolygon([cq.Vector(x, y, 0) for x, y in list(c)[:-1]], close=True)
        fc = cq.Face.makeFromWires(mk(q.exterior.coords), [mk(i.coords) for i in q.interiors])
        sol = cq.Solid.extrudeLinear(fc, cq.Vector(0, 0, depth + 0.5)).translate(cq.Vector(0, 0, z - depth))
        out = sol if out is None else out.fuse(sol)
    return cq.Workplane().add(out.clean())
def panel_inlay(base=None):
    """Flush 2nd-colour graphics: solids filling the outer face down to labels.INLAY_DEPTH."""
    global _inlay
    if _inlay is None:
        import labels
        g = labels.graphics(PANEL_OUT, labels.INLAY_DEPTH)
        if INLAY_MIN_STROKE:
            g = _thicken(g, PANEL_OUT, labels.INLAY_DEPTH, INLAY_MIN_STROKE)
        _inlay = g.intersect(base)
    return _inlay

# ------------------------------------------------------------------ back cover
def back_cover():
    c = rbox(OUT_W, OUT_H, R_OUT, Z_COVER_OUT, Z_COVER_IN)
    # locating lip inside the walls on left/right/bottom sides
    lip = rbox(IN_W - 0.6, IN_H - 0.6, R_IN - 0.3, Z_COVER_IN - 0.01, Z_COVER_IN + 1.5)
    lip = lip.cut(rbox(IN_W - 3.0, IN_H - 3.0, max(R_IN - 1.5, 0.5), Z_COVER_IN - 1, Z_COVER_IN + 2))
    lip = lip.cut(box(-5, -6, 105, 5, Z_COVER_IN - 1, Z_COVER_IN + 2))      # no lip along the connector wall
    c = c.union(lip)
    for x, yd in HOLES:
        c = c.union(cyl(x, yd, BOSS_OD, Z_COVER_IN - 0.01, 0.0))
        c = c.cut(cyl(x, yd, 3.4, Z_COVER_OUT - 1, 1))
        c = c.cut(cone(x, yd, 6.6, Z_COVER_OUT - 0.01, 3.4, Z_COVER_OUT + 1.6))   # 90deg countersink
    # tabs closing the rim side of the wall notches
    t = 0.2  # side clearance
    u = USB
    zc = (u["z0"] + u["z1"]) / 2
    if USBC_RELIEF == "pocket":
        c = c.union(box(u["x"] - u["w"]/2 - FIT + t, WALL_Y0, u["x"] + u["w"]/2 + FIT - t, WALL_Y0 + 0.8, Z_COVER_IN - 0.01, u["z0"] - FIT))
    y_tab = WALL_Y0 + 0.8 + 0.01 if USBC_RELIEF == "pocket" else WALL_Y0
    c = c.union(box(u["x"] - u["plug_w"]/2 - FIT + t, y_tab, u["x"] + u["plug_w"]/2 + FIT - t, WALL_Y1,
                    Z_COVER_IN - 0.01, zc - u["plug_h"]/2 - FIT))
    for x in SMA_X:
        fl = SMA_FLANGE + 2*FIT
        c = c.union(box(x - fl/2 + t, WALL_Y0, x + fl/2 - t, SMA_FLANGE_DEPTH + 0.2, Z_COVER_IN - 0.01, SMA_AXIS_Z - SMA_FLANGE/2 - FIT))
        rb = SMA_BARREL/2 + FIT
        c = c.union(box(x - rb + t, SMA_FLANGE_DEPTH + 0.2, x + rb - t, WALL_Y1, Z_COVER_IN - 0.01, SMA_AXIS_Z - SMA_FLANGE/2 - FIT))
    return c

def print_orient(part, name):
    """front shell: panel face down (flip about X); cover: outer face down. Returns solid on Z=0."""
    s = part.val() if hasattr(part, "val") else part
    if name == "front":
        s = s.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = s.BoundingBox()
    return s.translate(cq.Vector(-bb.center.x, -bb.center.y, -bb.zmin))

if __name__ == "__main__":
    f, b = front_shell(), back_cover()
    for name, part in (("front_shell", f), ("back_cover", b)):
        s = part.val()
        print(name, "valid", s.isValid(), "vol cm3", round(s.Volume()/1000, 2))
        cq.exporters.export(part, os.path.join(OUT, f"vfo_{name}_assembly_frame.step"))
        po = print_orient(s, "front" if name == "front_shell" else "cover")
        cq.exporters.export(po, os.path.join(OUT, f"vfo_{name}.step"))
        cq.exporters.export(po, os.path.join(OUT, f"vfo_{name}.stl"), tolerance=0.02, angularTolerance=0.1)
        bb = po.BoundingBox(); print(f"  print bbox {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
        if name == "front_shell" and PANEL_GRAPHICS == "inlay":
            ss = part.val(); ins = panel_inlay().val()
            bbf = ss.rotate((0,0,0),(1,0,0),180).BoundingBox()
            mv = lambda o: o.rotate((0,0,0),(1,0,0),180).translate(cq.Vector(-bbf.center.x, -bbf.center.y, -bbf.zmin))
            cq.exporters.export(po, os.path.join(OUT, "vfo_front_shell_body.stl"), tolerance=0.02, angularTolerance=0.1)
            ip = mv(ins)
            cq.exporters.export(ip, os.path.join(OUT, "vfo_front_shell_inlay.stl"), tolerance=0.01, angularTolerance=0.1)
            asm = cq.Assembly().add(po, name="body", color=cq.Color(0.1,0.1,0.1)).add(ip, name="inlay", color=cq.Color(1,1,1))
            asm.save(os.path.join(OUT, "vfo_front_shell_2color.step"))
            ib = ip.BoundingBox(); print("  inlay valid", ins.isValid(), "vol mm3", round(ins.Volume(),1), "z", round(ib.zmin,3), round(ib.zmax,3), "body+inlay vs base", round(po.Volume()+ip.Volume(),1), THIN_REPORT)
    sys.stdout.flush(); os._exit(0)
