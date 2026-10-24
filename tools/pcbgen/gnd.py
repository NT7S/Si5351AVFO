import pcbnew, sys
from pcbnew import VECTOR2I
PCB='/workspace/Si5351AVFO/PCB/Si5351AVFO.kicad_pcb'
b=pcbnew.LoadBoard(PCB); X0=Y0=100.0; M=pcbnew.FromMM
def P(x,y): return VECTOR2I(M(X0+x),M(Y0+y))
gnd=b.FindNet('GND'); gc=gnd.GetNetCode()
LAY=[pcbnew.F_Cu,pcbnew.B_Cu]
items=[]
for f in b.GetFootprints():
    for p in f.Pads(): items.append(p)
items+=list(b.GetTracks())
edge=[d for d in b.GetDrawings() if d.GetLayer()==pcbnew.Edge_Cuts]
def free(x,y,r=0.3,cl=0.2,tr=None):
    c=pcbnew.SHAPE_CIRCLE(P(x,y),M(r))
    if not(0.6<x<99.4 and 0.6<y<64.4): return False
    for it in items:
        if it.GetNetCode()==gc and it.GetClass()!='PAD': 
            if it.GetClass()=='PCB_VIA' and (it.GetPosition()-P(x,y)).EuclideanNorm()<M(0.75): return False
            continue
        for L in LAY:
            if it.IsOnLayer(L) and it.GetEffectiveShape(L).Collide(c,M(cl)) and it.GetNetCode()!=gc: return False
        if it.GetClass()=='PAD' and it.GetNetCode()==gc and it.GetEffectiveShape(pcbnew.F_Cu).Collide(c,0) and it.GetAttribute()!=pcbnew.PAD_ATTRIB_PTH: return False
        if it.HasHole() if hasattr(it,'HasHole') else False:
            hs=it.GetEffectiveHoleShape()
            if hs and hs.Collide(c,M(0.25)): return False
    if tr:
        s=pcbnew.SHAPE_SEGMENT(P(*tr[0]),P(*tr[1]),M(0.4))
        for it in items:
            if it.GetNetCode()!=gc and it.IsOnLayer(pcbnew.F_Cu) and it.GetEffectiveShape(pcbnew.F_Cu).Collide(s,M(0.2)): return False
    return True
def addvia(x,y):
    v=pcbnew.PCB_VIA(b); v.SetPosition(P(x,y)); v.SetWidth(M(0.6)); v.SetDrill(M(0.3)); v.SetNet(gnd); b.Add(v); items.append(v); return v
def addtrk(a,c):
    t=pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(M(0.4)); t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd); b.Add(t); items.append(t)
n=0; miss=[]
for f in b.GetFootprints():
    r=f.GetReference()
    if r.startswith(('H','SH','J2','J3','J4','LOGO')): continue
    fc=f.GetPosition()
    for p in f.Pads():
        if p.GetNetCode()!=gc or p.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD: continue
        q=p.GetPosition(); px,py=q.x/1e6-X0,q.y/1e6-Y0
        sz=p.GetBoundingBox(); hw,hh=sz.GetWidth()/2e6,sz.GetHeight()/2e6
        dx,dy=px-(fc.x/1e6-X0),py-(fc.y/1e6-Y0)
        cands=[]
        for d in (0.45,0.7,1.0,1.4):
            dirs=[]
            if abs(dx)>=abs(dy) and abs(dx)>1e-3: dirs.append((1 if dx>0 else -1,0))
            elif abs(dy)>1e-3: dirs.append((0,1 if dy>0 else -1))
            dirs+=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
            for ux,uy in dirs:
                cands.append((px+ux*(hw+d),py+uy*(hh+d)))
        ok=False
        for (vx,vy) in cands:
            if free(vx,vy,tr=((px,py),(vx,vy))):
                addtrk((px,py),(vx,vy)); addvia(vx,vy); n+=1; ok=True; break
        if not ok: miss.append(r+'.'+p.GetNumber())
print('decoupling/GND pad vias',n,'missed',miss)
# U3 (CP2102N QFN24): pin 2 GND tied straight into the exposed pad; EP gets 4 thermal vias to In1
t=pcbnew.PCB_TRACK(b); t.SetStart(P(25.5625,14.75)); t.SetEnd(P(26.6,14.75)); t.SetWidth(M(0.2)); t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd); b.Add(t); items.append(t)
for dx in (-0.65,0.65):
    for dy in (-0.65,0.65): addvia(27.5+dx,15.5+dy)
# stitching grid in the RF fence and around SMA launches
s=0
y=8.2
while y<39.0:
    x=52.8
    while x<91.5:
        if free(x,y,cl=0.45): addvia(x,y); s+=1
        x+=1.6
    y+=1.6
for sx in (58.0,71.0,84.0):
    for (vx,vy) in ((sx-2.4,5.6),(sx+2.4,5.6),(sx-1.6,6.0),(sx+1.6,6.0)):
        if free(vx,vy,cl=0.25): addvia(vx,vy); s+=1
print('stitch vias',s)
for t in b.GetTracks(): t.SetLocked(True)
b.Save(PCB)
