import pcbnew,math,sys
F='/workspace/Si5351AVFO/PCB/Si5351AVFO.kicad_pcb';b=pcbnew.LoadBoard(F);M=pcbnew.FromMM;V=lambda x,y:pcbnew.VECTOR2I(M(x),M(y))
g=b.FindNet('GND');gc=g.GetNetCode();VD=0.6;CL=0.25
layers=[pcbnew.F_Cu,pcbnew.In1_Cu,pcbnew.In2_Cu,pcbnew.B_Cu]
items=[p for f in b.GetFootprints() for p in f.Pads()]+[t for t in b.GetTracks()]
obs=[i for i in items if i.GetNetCode()!=gc]
gv=[t.GetPosition() for t in b.GetTracks() if isinstance(t,pcbnew.PCB_VIA)]
holes=[p.GetPosition() for f in b.GetFootprints() for p in f.Pads() if p.GetDrillSizeX()>0]
ko=[z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
edge=[d for d in b.GetDrawings() if d.GetLayer()==pcbnew.Edge_Cuts]
smd_g=[p for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode()==gc]
def ok(x,y,sp):
    p=V(x,y);c=pcbnew.SHAPE_CIRCLE(p,M(VD/2))
    for q in gv+holes:
        if math.hypot(q.x-p.x,q.y-p.y)<M(sp): return False
    for e in edge:
        if e.GetEffectiveShape().Collide(c,M(0.5)): return False
    for z in ko:
        if z.Outline().Collide(p,M(VD/2)): return False
    for i in obs:
        bb=i.GetBoundingBox()
        if abs(bb.Centre().x-p.x)>bb.GetWidth()/2+M(2) or abs(bb.Centre().y-p.y)>bb.GetHeight()/2+M(2): continue
        for l in layers:
            if i.IsOnLayer(l) and i.GetEffectiveShape(l).Collide(c,M(CL)): return False
    for i in smd_g:   # don't drop vias into GND SMD pads (keeps paste sane) except none
        if i.GetAttribute()==pcbnew.PAD_ATTRIB_SMD and i.GetEffectiveShape(pcbnew.F_Cu).Collide(c,0) : return False
    return True
added=0
def add(x,y,sp):
    global added
    if ok(x,y,sp):
        v=pcbnew.PCB_VIA(b);v.SetPosition(V(x,y));v.SetWidth(M(VD));v.SetDrill(M(0.3 if VD>0.55 else 0.25));v.SetNet(g);b.Add(v);gv.append(V(x,y));added+=1
mode=sys.argv[1]
if mode=='sma':
    for cx in (158,171,184):
        for r in (1.6,2.2,2.9,3.6):
            for a in range(0,181,15):
                x=cx+r*math.cos(math.radians(a));y=100+r*math.sin(math.radians(a))
                add(round(x,2),round(y,2),1.0)
if mode=='sma2':
    VD=0.5
    for cx in (158,171,184):
        for dx in (-1.75,1.75):
            for y in (101.0,101.8,102.6,103.4,104.2,105.0):
                add(cx+dx,y,0.9)
if mode=='fence':
    # along filter lanes inside the can: rows of vias parallel to lanes, pitch 1.5 mm
    xs=[float(v) for v in sys.argv[2].split(',')]
    for x0 in xs:
        y=107.5
        while y<139:
            for dx in (0,-0.3,0.3,-0.6,0.6):
                if ok(x0+dx,y,1.3): add(x0+dx,y,1.3);break
            y+=1.5
print('added',added);b.Save(F)
