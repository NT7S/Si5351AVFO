import os, sys, numpy as np, cadquery as cq, pyvista as pv, trimesh
import vfo_case as V
os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists("board.stl"):
    bd = cq.importers.importStep(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "mechanical", "Si5351AVFO_board.step"))
    cq.exporters.export(bd, "board.stl", tolerance=0.05, angularTolerance=0.2)
for n, p in (("front", V.front_shell()), ("cover", V.back_cover())):
    cq.exporters.export(p, f"_{n}_asm.stl", tolerance=0.02, angularTolerance=0.1)
B, F, C = pv.read("board.stl"), pv.read("_front_asm.stl"), pv.read("_cover_asm.stl")
def shot(fn, meshes, cam, size=(1600, 1100)):
    pl = pv.Plotter(off_screen=True, window_size=size); pl.set_background("white")
    for m, col, op in meshes: pl.add_mesh(m, color=col, opacity=op, smooth_shading=False, specular=0.2)
    pl.camera_position = cam; pl.camera.zoom(1.25 if "exploded" not in fn else 0.95); pl.enable_anti_aliasing("ssaa"); pl.screenshot(fn); pl.close()
iso_front = [(170, -150, 160), (50, -32, 4), (0, 0, 1)]
shot("vfo_case_assembled.png", [(B, "#2e7d32", 1), (F, "#e0e0e0", 0.55), (C, "#5c6bc0", 1)], [(-40, -150, 150), (50, -32, 4), (0, 0, 1)])
shot("vfo_case_assembled_front.png", [(B, "#2e7d32", 1), (F, "#cfcfcf", 1), (C, "#5c6bc0", 1)], [(50, -150, 140), (50, -32, 4), (0, 0, 1)])
shot("vfo_case_connectors.png", [(B, "#2e7d32", 1), (F, "#cfcfcf", 1), (C, "#5c6bc0", 1)], [(50, 130, 40), (50, -32, 2), (0, 0, 1)])
shot("vfo_case_exploded.png", [(B, "#2e7d32", 1), (F.translate((0, 0, 30)), "#cfcfcf", 1), (C.translate((0, 0, -25)), "#5c6bc0", 1)], [(-120, -260, 170), (50, -32, 0), (0, 0, 1)], (1400, 1500))
fp, cp = pv.read("../stl/vfo_front_shell.stl"), pv.read("../stl/vfo_back_cover.stl")
shot("vfo_case_front_print.png", [(fp, "#ff8f00", 1)], [(80, -120, 140), (0, 0, 5), (0, 0, 1)])
shot("vfo_case_cover_print.png", [(cp, "#ff8f00", 1)], [(80, -120, 140), (0, 0, 3), (0, 0, 1)])
sys.stdout.flush(); os._exit(0)
