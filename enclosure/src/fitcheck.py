import os, sys, numpy as np, cadquery as cq, trimesh
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
import vfo_case as V
board = cq.importers.importStep("repo/docs/mechanical/Si5351AVFO_board.step").val()
solids = board.Solids()
f, b = V.front_shell().val(), V.back_cover().val()
fence = V.dbox(51, 6.5, 93, 40, 1.6, 7.6).val()
oled_keep = V.dbox(8, 20, 47.4, 57.5, 1.6, V.GLASS_TOP_Z).val()
ex, ey = V.ENCODER
enc = (V.dbox(ex-5.85, ey-6, ex+5.85, ey+6, 1.6, V.ENC_BODY_TOP_Z)
       .union(V.cyl(ex, ey, 7.0, V.ENC_BODY_TOP_Z, V.ENC_BUSHING_TOP_Z))
       .union(V.cyl(ex, ey, 6.0, V.ENC_BUSHING_TOP_Z, V.ENC_SHAFT_TOP_Z))
       .union(V.dbox(ex-5, ey-7.5, ex+5, ey+7.5, -1.9, 0.0))).val()     # leads 3.5 below mounting surface
nutw = V.cyl(ex, ey, 12.0, V.ENC_BUSHING_TOP_Z - V.ENC_NUT_T - V.ENC_WASHER_T - V.ENC_THREAD_SPARE, V.ENC_BUSHING_TOP_Z - V.ENC_THREAD_SPARE).val()
TRIM_Z = V.MODULE_TOP_Z + 1.0   # DS1 header pins trimmed flush (1.0 mm solder joint allowance above module PCB)
solids[107] = solids[107].intersect(V.box(-5, -70, 105, 5, -5, TRIM_Z).val())
items = [(f"solid{i}", s) for i, s in enumerate(solids) if i != 30] + [("SH1_fence_env", fence), ("EC11E_datasheet_env", enc), ("M7_nut+washer_env", nutw)]
print("STEP encoder solid30 excluded (model shorter than datasheet); vs front vol:", round(f.intersect(solids[30]).Volume(),3))
def bbo(a, c, m=0.5):
    A, C = a.BoundingBox(), c.BoundingBox()
    return not (A.xmax+m < C.xmin or C.xmax+m < A.xmin or A.ymax+m < C.ymin or C.ymax+m < A.ymin or A.zmax+m < C.zmin or C.zmax+m < A.zmin)
def dist(a, c):
    d = BRepExtrema_DistShapeShape(a.wrapped, c.wrapped); d.Perform(); return d.Value()
res = []
for pn, p in (("front", f), ("cover", b)):
    for n, s in items:
        if not bbo(p, s, 3): continue
        v = p.intersect(s).Volume() if bbo(p, s, 0) else 0.0
        bb = s.BoundingBox()
        res.append((pn, n, v, dist(p, s), f"x{bb.xmin:.1f}-{bb.xmax:.1f} y{-bb.ymax:.1f}-{-bb.ymin:.1f} z{bb.zmin:.2f}-{bb.zmax:.2f}"))
bad = [r for r in res if r[2] > 1e-4]
print("INTERFERENCES:", len(bad)); [print("  ", r) for r in bad]
print("closest 25:")
for r in sorted(res, key=lambda r: r[3])[:25]: print(f"  {r[0]:5} {r[1]:14} vol={r[2]:.4f} d={r[3]:.3f} {r[4]}")
print("front vs cover overlap vol", round(f.intersect(b).Volume(), 4), "dist", round(dist(f, b), 3))
print("front within OLED keepout (vol, informational):", round(f.intersect(oled_keep).Volume(), 2))
for pn, p in (("front", "vfo_front_shell.stl"), ("cover", "vfo_back_cover.stl")):
    m = trimesh.load(p); n = m.face_normals; c = m.triangles_center; a = m.area_faces
    down = n[:, 2] < -np.cos(np.radians(44))
    onbed = c[:, 2] < 0.05
    flat = n[:, 2] < -0.999
    ov = down & ~onbed
    print(f"{pn}: watertight={m.is_watertight} extents={np.round(m.extents,2)} overhang>45 area off-bed={a[ov].sum():.2f} mm2 (flat ceilings {a[ov & flat].sum():.2f})")
    if ov.any():
        zs = np.round(c[ov, 2], 2); print("   overhang z levels:", sorted(set(zs.tolist()))[:20])
sys.stdout.flush(); os._exit(0)
