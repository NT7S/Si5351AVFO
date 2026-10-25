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
W=0.31
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
    c1,_=pad('C%d'%bs,'1'); trk([r2,(r2[0],c1[1])] if abs(r2[0]-c1[0])<0.7 else [r2,(c1[0],r2[1]),c1],W,F,n)
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
# Si5351 CLK fan-out: U2 rotated so CLK0/1/2 leave the top row on F.Cu, 0.25 neck at the pins into the 0402 series Rs
gnd=net('GND'); vc=net('+3V3_CLK')
(p10,n0)=pad('U2','10'); (p9,n1)=pad('U2','9'); (p6,n2)=pad('U2','6')
r0,_=pad('R100','1'); r1,_=pad('R120','1'); r2,_=pad('R140','1')
trk([(p10[0],p10[1]),(p10[0],r0[1]),r0],0.25,F,n0)
trk([(p9[0],p9[1]),r1],0.25,F,n1)
trk([p6,(p6[0],32.8),(p6[0]+(32.8-r2[1]),r2[1]),r2],0.25,F,n2)
# pin 8 GND into the body to a via; VDDO pin 7 -> C26 above and a +3V3_CLK via inside the body
(p8,_)=pad('U2','8'); trk([p8,(p8[0],33.9),(71.6,35.5)],0.25,F,gnd); via(71.6,35.5,gnd)
(p7,_)=pad('U2','7'); (c26,_)=pad('C26','1'); trk([c26,p7,(p7[0],34.6)],0.25,F,vc); via(p7[0],34.6,vc)
# VDD pin 1 <- C4 pad 1 <- +3V3_CLK via
(p1,_)=pad('U2','1'); (c4,_)=pad('C4','1'); trk([(68.4,p1[1]),(c4[0],p1[1]),p1],0.3,F,vc); via(68.4,p1[1],vc)
# XA under the bottom row to C6; I2C stubs out to the right of U2
(p2,nx)=pad('U2','2'); (c6,_)=pad('C6','2'); trk([p2,(p2[0],38.42),(c6[0],38.42),c6],0.2,F,nx)
# SCL is left to the autorouter from pin 4
(p5,nd)=pad('U2','5'); trk([p5,(p5[0],37.0),(74.6,37.0)],0.2,F,nd)
# bulk caps C27/C28: pads joined between them on F.Cu, one via to the In2 rail
(c27,_)=pad('C27','1'); (c28,_)=pad('C28','1'); my=(c27[1]+c28[1])/2
trk([c27,c28],0.4,F,vc); trk([(c27[0]-1.25,my),(c27[0],my)],0.4,F,vc); via(c27[0]-1.25,my,vc)
b.Save(PCB)
print('rf routed')
