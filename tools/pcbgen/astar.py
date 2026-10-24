# tiny grid A* router: python3 astar.py NET x0 y0 x1 y1 width LAYER[,LAYER2] (board coords, mm, origin 100,100)
import pcbnew,sys,heapq,math
F='/workspace/Si5351AVFO/PCB/Si5351AVFO.kicad_pcb'; b=pcbnew.LoadBoard(F)
net,x0,y0,x1,y1,w,lays=sys.argv[1],*map(float,sys.argv[2:7]),sys.argv[7].split(',')
M=pcbnew.FromMM; O=100; G=0.1; CL=0.2
nc=b.FindNet(net).GetNetCode(); L=[b.GetLayerID(l) for l in lays]
items=[p for f in b.GetFootprints() for p in f.Pads()]+list(b.GetTracks())
zones=[z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowTracks()]
edge=[d for d in b.GetDrawings() if d.GetLayer()==pcbnew.Edge_Cuts]
obs={l:[(i,i.GetEffectiveShape(l)) for i in items if i.GetNetCode()!=nc and i.IsOnLayer(l)] for l in L}
holes=[p for f in b.GetFootprints() for p in f.Pads() if p.GetDrillSizeX()>0 and p.GetNetCode()!=nc]
cache={}
def free(ix,iy,li,r):
    k=(ix,iy,li,r)
    if k in cache: return cache[k]
    p=pcbnew.VECTOR2I(M(ix*G+O),M(iy*G+O)); l=L[li]; ok=True
    c=pcbnew.SHAPE_CIRCLE(p,M(r))
    for i,s in obs[l]:
        bb=i.GetBoundingBox()
        if abs(bb.Centre().x-p.x)>bb.GetWidth()/2+M(r+CL+0.5) or abs(bb.Centre().y-p.y)>bb.GetHeight()/2+M(r+CL+0.5): continue
        if s.Collide(c,M(CL)): ok=False;break
    if ok:
        for z in zones:
            if z.IsOnLayer(l) and z.Outline().Collide(p,M(r+0.05)): ok=False;break
    if ok:
        for e in edge:
            if e.GetEffectiveShape().Collide(c,M(0.3)): ok=False;break
    cache[k]=ok; return ok
s=(round(x0/G),round(y0/G),0); g=(round(x1/G),round(y1/G))
VR=0.3
def h(n): return math.hypot(n[0]-g[0],n[1]-g[1])
pq=[(h(s),0,s)]; prev={s:None}; cost={s:0}; near=lambda n:math.hypot(n[0]-s[0],n[1]-s[1])<6 or h(n)<6
D=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]; found=None; it=0
while pq and it<400000:
    _,c,n=heapq.heappop(pq); it+=1
    if (n[0],n[1])==g and n[2]==len(L)-1 or ((n[0],n[1])==g and len(L)==1): found=n;break
    nb=[((n[0]+dx,n[1]+dy,n[2]),math.hypot(dx,dy)) for dx,dy in D]
    if len(L)>1: nb.append(((n[0],n[1],1-n[2]),20))
    for m,sc in nb:
        if m in cost and cost[m]<=c+sc: continue
        if m[2]!=n[2]:
            if not all(free(m[0],m[1],li,VR) for li in range(len(L))): continue
        elif not (near(m) or free(m[0],m[1],m[2],w/2)): continue
        cost[m]=c+sc; prev[m]=n; heapq.heappush(pq,(c+sc+h(m),c+sc,m))
if not found: print('NOROUTE',it); sys.exit(1)
path=[];n=found
while n: path.append(n); n=prev[n]
path.reverse()
# simplify into segments
segs=[];st=path[0]
for i in range(1,len(path)):
    a=path[i-1];c=path[i]
    if c[2]!=a[2]:
        segs.append((st,a));st=c
        v=pcbnew.PCB_VIA(b);v.SetPosition(pcbnew.VECTOR2I(M(c[0]*G+O),M(c[1]*G+O)));v.SetWidth(M(0.6));v.SetDrill(M(0.3));v.SetNet(b.FindNet(net));b.Add(v)
        continue
    if i+1<len(path):
        d=path[i+1]
        if d[2]==c[2] and (d[0]-c[0],d[1]-c[1])==(c[0]-a[0],c[1]-a[1]): continue
    segs.append((st,c));st=c
for a,c in segs:
    if a[:2]==c[:2]: continue
    t=pcbnew.PCB_TRACK(b);t.SetStart(pcbnew.VECTOR2I(M(a[0]*G+O),M(a[1]*G+O)));t.SetEnd(pcbnew.VECTOR2I(M(c[0]*G+O),M(c[1]*G+O)))
    t.SetWidth(M(w));t.SetLayer(L[a[2]]);t.SetNet(b.FindNet(net));b.Add(t)
b.Save(F); print('routed',len(segs),'segs',it,'iters')
