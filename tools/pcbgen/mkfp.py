import pcbnew
LIB='/workspace/Si5351AVFO/PCB/lib/Etherkit.pretty'
b=pcbnew.LoadBoard('/workspace/ref/EtherKeyerMini/PCB/EtherKeyerMini.kicad_pcb')
class _IO:
    def FootprintSave(self,lib,f): pcbnew.FootprintSave(lib,f)
io=_IO()
for f in b.GetFootprints():
    n=f.GetFPID().GetLibItemName()
    if n in ('OSHWLogo4mm',):
        print(n,f.GetLayerName(),[g.GetLayerName() for g in f.GraphicalItems()][:3])
        g=pcbnew.FOOTPRINT(f); g.SetPosition(pcbnew.VECTOR2I(0,0)); g.SetOrientationDegrees(0)
        io.FootprintSave(LIB,g)
    if n=='EtherkitLogoSmall': print(n,[g.GetLayerName() for g in f.GraphicalItems()][:3])
# RF fence: outer rect W x H, 1.0 mm strip, gaps at SMA notches (top wall), vias 2.5mm pitch
M=pcbnew.FromMM
W,H=42.0,33.5; S=1.0; GAPS=[7.0,20.0,33.0]; GW=2.4   # gap centres along top wall, from left
f=pcbnew.FOOTPRINT(b); f.SetFPID(pcbnew.LIB_ID('EtherkitKicadLibrary','RF_Fence_42x33.5mm'))
f.SetAttributes(pcbnew.FP_SMD|pcbnew.FP_EXCLUDE_FROM_BOM|pcbnew.FP_EXCLUDE_FROM_POS_FILES)
f.SetLibDescription('DNP solder fence for a cut tin-plate RF shield: 1.0 mm exposed GND strip, 42 x 33.5 mm outer, 2.4 mm notches for the 3 SMA feed lines, 0.3/0.6 mm GND vias at <=2.5 mm pitch')
def pad(x0,y0,x1,y1):
    p=pcbnew.PAD(f); p.SetNumber('1'); p.SetShape(pcbnew.PAD_SHAPE_RECT); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    ls=pcbnew.LSET(); [ls.AddLayer(l) for l in (pcbnew.F_Cu,pcbnew.F_Mask)]; p.SetLayerSet(ls)
    p.SetSize(pcbnew.VECTOR2I(M(x1-x0),M(y1-y0))); p.SetPosition(pcbnew.VECTOR2I(M((x0+x1)/2),M((y0+y1)/2))); f.Add(p)
def via(x,y):
    p=pcbnew.PAD(f); p.SetNumber('1'); p.SetShape(pcbnew.PAD_SHAPE_CIRCLE); p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    p.SetLayerSet(pcbnew.PAD.PTHMask()); ls=p.GetLayerSet(); ls.RemoveLayer(pcbnew.F_Mask); ls.RemoveLayer(pcbnew.B_Mask); p.SetLayerSet(ls)
    p.SetSize(pcbnew.VECTOR2I(M(0.6),M(0.6))); p.SetDrillSize(pcbnew.VECTOR2I(M(0.3),M(0.3))); p.SetPosition(pcbnew.VECTOR2I(M(x),M(y))); f.Add(p)
import math
def run(x0,y0,x1,y1):
    pad(x0,y0,x1,y1); L=max(x1-x0,y1-y0); n=max(1,math.ceil((L-1.0)/2.5)); 
    for i in range(n+1):
        t=0.5+(L-1.0)*i/n
        via(x0+t,(y0+y1)/2) if x1-x0>y1-y0 else via((x0+x1)/2,y0+t)
# top wall with gaps
xs=[0]+sum([[g-GW/2,g+GW/2] for g in GAPS],[])+[W]
for i in range(0,len(xs),2): run(xs[i],0,xs[i+1],S)
run(0,H-S,W,H); run(0,S,S,H-S); run(W-S,S,W,H-S)
for l,(a,c) in ((pcbnew.F_Fab,((0,0),(W,H))),):
    r=pcbnew.PCB_SHAPE(f); r.SetShape(pcbnew.SHAPE_T_RECT); r.SetLayer(l); r.SetStart(pcbnew.VECTOR2I(M(0),M(0))); r.SetEnd(pcbnew.VECTOR2I(M(W),M(H))); r.SetWidth(M(0.1)); f.Add(r)
f.Reference().SetPosition(pcbnew.VECTOR2I(M(W/2),M(H+1.2))); f.Reference().SetLayer(pcbnew.F_Fab); f.Value().SetLayer(pcbnew.F_Fab)
f.Value().SetText('RF_FENCE')
io.FootprintSave(LIB,f); print('fence pads',len(f.Pads()))
