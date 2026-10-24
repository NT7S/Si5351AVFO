import pcbnew, math, sys
from pcbnew import VECTOR2I
PCB='/workspace/Si5351AVFO/PCB/Si5351AVFO.kicad_pcb'
b=pcbnew.LoadBoard(PCB)
X0=Y0=100.0
M=pcbnew.FromMM
def P(x,y): return VECTOR2I(M(X0+x),M(Y0+y))
F,B=pcbnew.F_Cu,pcbnew.B_Cu
def net(n): return b.FindNet(n)
PD={}
for f in b.GetFootprints():
    for p in f.Pads():
        q=p.GetPosition(); PD.setdefault((f.GetReference(),p.GetNumber()),((q.x/1e6-X0,q.y/1e6-Y0),p.GetNetname()))
def pad(ref,num):
    xy,n=PD[(ref,num)]; return xy,b.FindNet(n)
def trk(pts,w,layer,nt):
    for a,c in zip(pts,pts[1:]):
        t=pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(M(w)); t.SetLayer(layer); t.SetNet(nt); b.Add(t)
def via(x,y,nt,d=0.6,dr=0.3):
    v=pcbnew.PCB_VIA(b); v.SetPosition(P(x,y)); v.SetWidth(M(d)); v.SetDrill(M(dr)); v.SetNet(nt); b.Add(v); return v
W=0.35
SMAX=(58.0,71.0,84.0)
# remove via-fence vias that sit on the A-node and J-In crossings
for t in list(b.GetTracks()):
    if t.GetClass()=='PCB_VIA':
        x,y=t.GetPosition().x/1e6-X0,t.GetPosition().y/1e6-Y0
        if any(abs(x-(sx+3.6))<0.05 and (abs(y-8.6)<0.05 or abs(y-26.6)<0.05) for sx in SMAX): b.Remove(t)
def p2p(a,c,layer=F,w=W):
    (pa,na),(pc,_)=pad(*a),pad(*c)
    if abs(pa[0]-pc[0])<1e-3 or abs(pa[1]-pc[1])<1e-3: trk([pa,pc],w,layer,na)
    else: trk([pa,(pc[0],pa[1]),pc] if abs(pa[1]-pc[1])<abs(pa[0]-pc[0]) else [pa,(pa[0],pc[1]),pc],w,layer,na)
for ci,x in enumerate(SMAX):
    bs=100+20*ci; J='J%d'%(ci+2); L=['L%d'%(3*ci+j) for j in (1,2,3)]
    jp=lambda k:'JP%d'%(bs+k)
    # series chain (bottom -> top)
    (r2,n),_=pad('R%d'%bs,'2'),0
    c1,_=pad('C%d'%bs,'1'); trk([r2,(c1[0],r2[1]),c1] if abs(r2[0]-c1[0])>0.01 else [r2,c1],W,F,n)
    p2p(('C%d'%bs,'2'),(jp(2),'1'))
    p2p((jp(2),'2'),(L[0],'1')); p2p((L[0],'2'),(L[1],'1')); p2p((L[1],'2'),(L[2],'1')); p2p((L[2],'2'),(jp(3),'1'))
    p2p((jp(3),'2'),(J,'1'))
    # parallel caps (same y as L pads -> short horizontal stubs to the L pads)
    for l,c in zip(L,('C%d'%(bs+5),'C%d'%(bs+6),'C%d'%(bs+7))):
        for pn in ('1','2'):
            (cp,nn),(lp,_)=pad(c,pn),pad(l,pn); trk([cp,(lp[0],cp[1])],W,F,nn)
    # shunts: pad1 (signal) to the chain line, pad2 to GND via
    for s in ['C%d'%(bs+k) for k in (1,2,3,4)]+['R%d'%(bs+1)]:
        (sp,nn)=pad(s,'1'); trk([sp,(x,sp[1])],W,F,nn)
    # bypass: A node -> JPx4, lane JPx4 -> JPx5, JPx5 -> J-In
    (a,na)=pad(jp(2),'1'); (b4,_)=pad(jp(4),'1'); trk([a,b4],W,F,na)
    p2p((jp(4),'2'),(jp(5),'1'))
    (b5,nj)=pad(jp(5),'2'); (j3,_)=pad(jp(3),'2'); trk([b5,j3],W,F,nj)
# Si5351 CLK fan-out (0.25 neck at 0.5 mm pitch pins, then 0.35)
gnd=net('GND')
(p10,n0)=pad('U2','10'); (p9,n1)=pad('U2','9'); (p6,n2)=pad('U2','6')
r0,_=pad('R100','1'); r1,_=pad('R120','1'); r2,_=pad('R140','1')
trk([p10,(73.9,p10[1]),(74.5,34.9)],0.25,F,n0); trk([(74.5,34.9),(74.5,34.4)],W,F,n0); via(74.5,34.4,n0)
trk([(74.5,34.4),(72.6,34.4),(57.6,34.4),(55.9,32.7),(55.9,32.5)],W,B,n0); via(55.9,32.5,n0); trk([(55.9,32.5),r0],W,F,n0)
trk([p9,(74.4,p9[1])],0.25,F,n1); trk([(74.4,p9[1]),(75.4,35.0),(75.4,33.3),r1],W,F,n1)
trk([p6,(73.9,p6[1]),(74.6,38.2)],0.25,F,n2); trk([(74.6,38.2),(74.6,38.3)],W,F,n2); via(74.6,38.3,n2)
trk([(74.6,38.3),(81.4,38.3),(81.9,37.8),(81.9,32.5)],W,B,n2); via(81.9,32.5,n2); trk([(81.9,32.5),r2],W,F,n2)
(p8,_)=pad('U2','8'); trk([p8,(71.0,36.5)],0.3,F,gnd); via(71.0,36.5,gnd)
# return vias beside each RF layer change
for (vx,vy) in ((75.4,36.9),(73.6,33.6),(54.9,32.5),(80.9,32.5)):
    via(vx,vy,gnd)
b.Save(PCB)
print('rf routed')
