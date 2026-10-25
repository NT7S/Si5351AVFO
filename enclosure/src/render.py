"""Render the preview PNGs in ../renders from the current design (two-color front: black body, white inlay)."""
import os, sys, cadquery as cq, pyvista as pv
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)
import vfo_case as V
R = os.path.join(HERE, "..", "renders")
if not os.path.exists("board.stl"):
    bd = cq.importers.importStep(os.path.join(HERE, "..", "..", "docs", "mechanical", "Si5351AVFO_board.step"))
    cq.exporters.export(bd, "board.stl", tolerance=0.05, angularTolerance=0.2)
front = V.front_shell()
parts = [("front", front), ("cover", V.back_cover())]
if V.PANEL_GRAPHICS == "inlay":
    parts.append(("inlay", V.panel_inlay(front)))
for n, p in parts:
    cq.exporters.export(p, f"_{n}_asm.stl", tolerance=0.01, angularTolerance=0.1)
B, F, C = pv.read("board.stl"), pv.read("_front_asm.stl"), pv.read("_cover_asm.stl")
I = pv.read("_inlay_asm.stl") if os.path.exists("_inlay_asm.stl") and V.PANEL_GRAPHICS == "inlay" else None
BODY, INK, BOARD, COVER = "#1c1c1c", "#ffffff", "#2e7d32", "#3a3a3a"
def front_meshes(dz=0, op=1):
    m = [(F.translate((0, 0, dz)), BODY, op)]
    if I is not None: m.append((I.translate((0, 0, dz)), INK, 1))
    return m
def shot(fn, meshes, cam, size=(1600, 1100), zoom=1.25, bg="#e8e8e8"):
    pl = pv.Plotter(off_screen=True, window_size=size); pl.set_background(bg)
    for m, col, op in meshes: pl.add_mesh(m, color=col, opacity=op, smooth_shading=False, specular=0.2)
    pl.camera_position = cam; pl.camera.zoom(zoom); pl.enable_anti_aliasing("ssaa"); pl.screenshot(os.path.join(R, fn)); pl.close()
shot("vfo_case_assembled.png", [(B, BOARD, 1)] + front_meshes(op=0.45) + [(C, COVER, 1)], [(-40, -150, 150), (50, -32, 4), (0, 0, 1)])
shot("vfo_case_assembled_front.png", [(B, BOARD, 1)] + front_meshes() + [(C, COVER, 1)], [(50, -150, 140), (50, -32, 4), (0, 0, 1)])
shot("vfo_case_connectors.png", [(B, BOARD, 1)] + front_meshes() + [(C, COVER, 1)], [(50, 130, 40), (50, -32, 2), (0, 0, 1)])
shot("vfo_case_exploded.png", [(B, BOARD, 1)] + front_meshes(30) + [(C.translate((0, 0, -25)), COVER, 1)], [(-120, -260, 170), (50, -32, 0), (0, 0, 1)], (1400, 1500), 0.95)
# panel close-ups: straight on and 3/4
shot("vfo_case_labels2_front.png", front_meshes(), [(50, -32.5, 250), (50, -32.5, 0), (0, 1, 0)], zoom=1.45)
shot("vfo_case_labels2_34.png", front_meshes(), [(130, -150, 150), (50, -32.5, 5), (0, 0, 1)], zoom=1.3)
# print orientation (from ../stl)
S = os.path.join(HERE, "..", "stl")
fb, fi, cp = (pv.read(os.path.join(S, f)) for f in ("vfo_front_shell_body.stl", "vfo_front_shell_inlay.stl", "vfo_back_cover.stl"))
shot("vfo_case_front_print.png", [(fb, BODY, 1), (fi, INK, 1)], [(80, -120, 140), (0, 0, 5), (0, 0, 1)])
shot("vfo_case_cover_print.png", [(cp, BODY, 1)], [(80, -120, 140), (0, 0, 3), (0, 0, 1)])
sys.stdout.flush(); os._exit(0)
