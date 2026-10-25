import pcbnew, re, sys
from pcbnew import VECTOR2I, FromMM as M
PROJ='/workspace/Si5351AVFO/PCB/'
OUT=PROJ+'Si5351AVFO.kicad_pcb'
FP='/app/extensions/Library/Footprints/footprints/'
# ---- sexpr parse
def parse(s):
    toks=re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+',s); st=[[]]
    for t in toks:
        if t=='(': st.append([])
        elif t==')': x=st.pop(); st[-1].append(x)
        else: st[-1].append(t[1:-1].replace('\\"','"') if t.startswith('"') else t)
    return st[0][0]
def get(l,k):
    for x in l:
        if isinstance(x,list) and x and x[0]==k: return x
def getall(l,k): return [x for x in l if isinstance(x,list) and x and x[0]==k]
net=parse(open('/workspace/build/net.net').read())
comps={}
for c in getall(get(net,'components'),'comp'):
    ref=get(c,'ref')[1]
    d=dict(value=get(c,'value')[1],fp=get(c,'footprint')[1],
           path=get(get(c,'sheetpath'),'tstamps')[1]+get(c,'tstamps')[1],
           props={get(p,'name')[1]:get(p,'value')[1] if get(p,'value') else '' for p in getall(c,'property')},
           fields={f[1][1]:(f[2] if len(f)>2 else '') for f in getall(get(c,'fields') or [],'field')},
           sheet=get(get(c,'sheetpath'),'names')[1],desc=(get(c,'description') or ['',''])[1],ds=(get(c,'datasheet') or ['',''])[1])
    comps[ref]=d
pinnet={}
nets=[]
for n in getall(get(net,'nets'),'net'):
    name=get(n,'name')[1]; nets.append(name)
    for nd in getall(n,'node'): pinnet[(get(nd,'ref')[1],get(nd,'pin')[1])]=name
# ---- board
b=pcbnew.NewBoard(OUT)
b.SetCopperLayerCount(4)
ni={}
for name in nets:
    it=pcbnew.NETINFO_ITEM(b,name); b.Add(it); ni[name]=it
W,H=100.0,65.0; X0,Y0=100.0,100.0
def P(x,y): return VECTOR2I(M(X0+x),M(Y0+y))
# placement table: ref -> (x,y,rot) board-relative mm
pl={}
# Rev: connectors on TOP edge (y=0). OLED bottom-left, buttons column, encoder bottom-right.
OX,OY=10.0,22.0
pl['DS1']=(OX+10.08,OY+2.0,90)
for i,x in enumerate((15.0,27.7,40.4)): pl['SW%d'%(i+2)]=(x,61.0,0)   # row centred under OLED active area (x=27.7)
ENC=(89.0,50.0)
pl['SH1']=(51.0,6.5,0)
pl['SW1']=(ENC[0]-7.5,ENC[1]-2.5,0)
SMAX=(58.0,71.0,84.0)
for i,x in enumerate(SMAX): pl['J%d'%(i+2)]=(x,0.0,180)
pl['J1']=(16.0,3.7,180)
for i,(x,y) in enumerate(((4,4),(W-4,4),(4,H-4),(W-4,H-4))): pl['H%d'%(i+1)]=(x,y,0)
pl['U2']=(71.0,36.5,0); pl['X1']=(63.5,37.0,0)
# Si5351 decoupling tight to pins: C4 at VDD pin1, X1 VDD filter R5/C5, EN pull-up R6, XA coupling C6
pl.update({'C4':(69.8,33.7,0),'C6':(66.65,35.6,90),'R5':(63.6,34.0,0),'C5':(59.6,34.5,0),'R6':(59.6,37.3,90)})
# Power/USB: CC R at J1, ESD under J1, CP2102N with its caps; LDO rows C_in-U-C_out-FB
pl.update({'R1':(18.9,10.6,90),'R2':(13.1,10.6,90),'D1':(16.0,10.3,0),'C10':(9.6,10.8,90),'C11':(9.6,14.2,90),
 'U3':(27.5,15.5,0),'C12':(23.2,14.0,90),'C13':(23.2,17.4,90),'R9':(25.8,19.1,0),'R7':(28.8,19.1,0),'R8':(31.8,19.1,0),
 'C1':(34.4,11.0,90),'U1':(37.5,11.0,0),'C2':(37.5,14.0,0),'C3':(40.6,11.0,90),'FB1':(43.0,11.0,90),
 'C7':(34.4,16.8,90),'U5':(37.5,16.8,0),'C8':(37.5,19.6,0),'C9':(40.6,16.8,90),'FB2':(43.0,16.8,90),
 'C22':(16.4,24.0,0),'C23':(12.8,24.0,0),'C24':(6.8,24.8,90),'J5':(46.8,10.0,0)})
pl['U4']=(64.5,49.2,0); pl['C15']=(64.5,41.4,0); pl['C16']=(68.4,41.4,0); pl['R13']=(55.6,42.8,0); pl['R12']=(55.6,45.2,0); pl['R29']=(55.6,47.6,0); pl['C25']=(55.6,50.0,0); pl['C21']=(55.6,52.4,0); pl['R18']=(55.6,54.8,0); pl['D4']=(51.0,42.8,0); pl['C14']=(51.0,45.2,0); pl['R19']=(51.0,50.0,0); pl['R20']=(51.0,52.4,0); pl['R25']=(51.0,54.8,0); pl['C17']=(72.6,42.8,0); pl['R14']=(72.6,45.2,0); pl['C18']=(72.6,47.6,0); pl['R15']=(72.6,50.0,0); pl['C19']=(72.6,52.4,0); pl['R16']=(72.6,54.8,0); pl['R21']=(77.0,42.8,0); pl['R17']=(77.0,45.2,0); pl['R22']=(77.0,47.6,0); pl['C20']=(77.0,50.0,0); pl['R23']=(77.0,52.4,0); pl['R24']=(77.0,54.8,0);  pl['R27']=(54.0,34.5,0); pl['R28']=(78.0,34.5,0)
chan={0:(SMAX[0],'0','10'),1:(SMAX[1],'2','12'),2:(SMAX[2],'4','14')}
# Straight-line LPF per channel, bottom (Si5351) -> top (SMA):
# R1x0 -> C1x0 -> [A] -> JPx2 in-select -> L(x1)||C(x5) -> L(x2)||C(x6) -> L(x3)||C(x7) -> JPx3 out-select -> SMA
# shunts (R1x1 at A, Cx1..Cx4 at ladder nodes) on the left; bypass JPx4 on the right at the input end,
# behind a GND via fence, its output leg runs up a guarded lane to the SMA.
LPF_VIAS=[]
for ci,(x,_,_) in chan.items():
    base=100+20*ci
    L=['L%d'%(3*ci+j) for j in (1,2,3)]
    pl['JP%d'%(base+3)]=(x,9.4,90)
    for k,(l,cp) in enumerate(zip(L[::-1],['C%d'%(base+7),'C%d'%(base+6),'C%d'%(base+5)])):
        y=13.35+k*4.25; pl[l]=(x,y,90); pl[cp]=(x+2.4,y,90)
    pl['JP%d'%(base+2)]=(x,26.0,90); pl['C%d'%base]=(x,29.5,90)
    pl['R%d'%base]=(x+(2.3 if ci==1 else 0),32.5,180 if ci==1 else 0)
    for k,r in enumerate(['C%d'%(base+4),'C%d'%(base+3),'C%d'%(base+2),'C%d'%(base+1)]): pl[r]=(x-3.2,11.25+k*4.25,180)
    pl['R%d'%(base+1)]=(x-3.2,27.85,180)
    pl['JP%d'%(base+4)]=(x+4.9,26.0,90); pl['JP%d'%(base+5)]=(x+4.9,9.4,90)
    y=8.6
    while y<=30.0: LPF_VIAS.append((x+3.6,y)); y+=1.5
# U2 rotated 90: CLK0/CLK1/CLK2 (pins 10/9/6) on the top row, each with its 0402 series R at the pin and a straight F.Cu CPWG to its channel
pl.update({'U2':(72.0,35.3,90),'R100':(69.0,32.25,180),'R120':(71.02,31.5,180),'R140':(74.9,31.9,0),
 'C26':(72.5,31.45,90),'C4':(69.3,36.2,90),'C6':(66.65,35.6,270),'C27':(42.05,4.9,180),'C28':(42.05,7.0,180)})
def load(fpid):
    lib,name=fpid.split(':')
    p=PROJ+'lib/Etherkit.pretty' if lib=='EtherkitKicadLibrary' else FP+lib+'.pretty'
    f=pcbnew.FootprintLoad(p,name); f.SetFPID(pcbnew.LIB_ID(lib,name)); return f
fps={}
for r,c in comps.items():
    f=load(c['fp']); f.SetReference(r); f.SetValue(c['value'])
    f.SetPath(pcbnew.KIID_PATH(c['path']))
    f.SetSheetname(c['props'].get('Sheetname','')); f.SetSheetfile(c['props'].get('Sheetfile',''))
    for k,v in c['fields'].items():
        if k in ('Footprint','Datasheet','Description','Value','Reference'): continue
        f.SetField(k,v)
    f.SetField('Description',c['desc']); f.SetField('Datasheet',c['ds'])
    if 'dnp' in c['props']: f.SetDNP(True)
    if "exclude_from_bom" in c["props"]: f.SetExcludedFromBOM(True)
    if "exclude_from_pos_files" in c["props"]: f.SetExcludedFromPosFiles(True)
    if 'exclude_from_board' in c['props']: f.SetBoardOnly(False)
    for p in f.Pads():
        n=pinnet.get((r,p.GetNumber()))
        if n: p.SetNet(ni[n])
    for fld in f.GetFields():
        if not fld.IsReference(): fld.SetVisible(False)
        else:
            fld.SetTextSize(VECTOR2I(M(0.8),M(0.8))); fld.SetTextThickness(M(0.12))
    mm={'RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm':'EC11E_Vertical_H20_simple','SW_Push_6x6mm_SMD_KH-6X6X11H-STM':'SW_6x6_H11_simple',
        'USB_C_Receptacle_HCTL_HC-TYPE-C-16P-01A':'USB_C_HCTL_HC-TYPE-C-16P-01A_simple','Oscillator_SMD_SeikoEpson_SG8002CE-4Pin_3.2x2.5mm':'Osc_3.2x2.5_simple',
        'SMA-ENDLAUNCH':'SMA_EndLaunch_simple','RF_Fence_42x33.5mm':'RF_Fence_42x33.5_can_simple'}.get(c['fp'].split(':')[1])
    if r=='DS1': mm='OLED_1.3in_SH1106_on_header_simple'
    if mm:
        if r!='DS1': f.Models().clear()
        md=pcbnew.FP_3DMODEL(); md.m_Filename='${KIPRJMOD}/lib/Etherkit.3dshapes/'+mm+'.step'
        if r=='SW1':  # Alps vendor model (EC11E-15SW.STEP from EC11E18244A5 zip): origin at shaft axis, seating plane z=-3.60
            md.m_Filename='${KIPRJMOD}/lib/Etherkit.3dshapes/Alps_EC11E18244A5.step'
            md.m_Offset=pcbnew.VECTOR3D(7.5,-2.5,3.6); md.m_Rotation=pcbnew.VECTOR3D(0,0,90)
        f.Models().append(md)
    if r.startswith('H'):
        for fld in f.GetFields(): fld.SetVisible(False)
        for g in list(f.GraphicalItems()):
            if g.GetLayer() in (pcbnew.F_SilkS,pcbnew.B_SilkS): f.Remove(g)
    fps[r]=f
    for fld in f.GetFields():
        if fld.GetText()==r and fld.IsVisible(): pass
    b.Add(f)

regions={'Power and USB':[(8,8,48,25),(22,0.5,48,8)],'MCU and UI':[(48,40.5,80,64.5),(8,8,48,25),(80,40.5,98,44),(0.5,8,8,40)],'Synth and RF outputs':[(52,33.5,92,39.5),(52,7.5,92,39.5)]}
boxes=[]
def bbox(f):
    c=f.GetCourtyard(pcbnew.F_CrtYd)
    bb=c.BBox() if c.OutlineCount() else f.GetBoundingBox(False)
    return [pcbnew.ToMM(v) for v in (bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom())]
def ov(a,b,cl=0.2): return not(a[2]+cl<=b[0] or b[2]+cl<=a[0] or a[3]+cl<=b[1] or b[3]+cl<=a[1])
keep=[X0+OX-2,Y0+OY-2,X0+OX+37.4,Y0+OY+35.5]
for r,f in fps.items():
    if r in pl:
        x,y,rot=pl[r]; f.SetPosition(P(x,y)); f.SetOrientationDegrees(rot)
        if r=='SH1':
            fx,fy=X0+x,Y0+y
            boxes.extend([[fx,fy,fx+42,fy+1],[fx,fy+32.5,fx+42,fy+33.5],[fx,fy,fx+1,fy+33.5],[fx+41,fy,fx+42,fy+33.5]])
        else: boxes.append(bbox(f))
def key(r): m=re.match(r'([A-Z]+)(\d+)',r); return (m.group(1),int(m.group(2)))
for r in sorted([r for r in fps if r not in pl],key=key):
    sh=comps[r]['sheet'].strip('/').split('/')[-1]; f=fps[r]; ok=False
    for (x0,y0,x1,y1) in regions[sh]:
        y=y0
        while y<y1 and not ok:
            x=x0
            while x<x1 and not ok:
                f.SetPosition(P(x,y)); bb=bbox(f)
                if bb[0]>=X0+x0 and bb[2]<=X0+x1 and bb[1]>=Y0+y0 and bb[3]<=Y0+y1 and not ov(bb,keep,0) and not any(ov(bb,o) for o in boxes):
                    ok=True; boxes.append(bb); pl[r]=(x,y,0)
                x+=0.5
            y+=0.5
    if not ok: print('NOFIT',r)
# outline with 3mm corner radius
R=3.0
def seg(a,bb):
    s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
    s.SetStart(P(*a)); s.SetEnd(P(*bb)); s.SetWidth(M(0.1)); b.Add(s)
def arc(c,st,ang):
    s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetLayer(pcbnew.Edge_Cuts)
    s.SetCenter(P(*c)); s.SetStart(P(*st)); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang,pcbnew.DEGREES_T),True); s.SetWidth(M(0.1)); b.Add(s)
seg((R,0),(W-R,0)); seg((W,R),(W,H-R)); seg((W-R,H),(R,H)); seg((0,H-R),(0,R))
arc((W-R,R),(W-R,0),90); arc((W-R,H-R),(W,H-R),90); arc((R,H-R),(R,H),90); arc((R,R),(0,R),90)
# OLED keepout: module 35.4x33.5 at (OX,OY) + 2mm => rule area: no footprints/tracks/vias on F side
def zone_rect(x0,y0,x1,y1,name,layers,fp=True,tr=False,via=False,pour=False):
    z=pcbnew.ZONE(b); z.SetIsRuleArea(True); z.SetZoneName(name)
    ls=pcbnew.LSET(); [ls.AddLayer(l) for l in layers]; z.SetLayerSet(ls)
    z.SetDoNotAllowFootprints(fp); z.SetDoNotAllowTracks(tr); z.SetDoNotAllowVias(via); z.SetDoNotAllowZoneFills(pour); z.SetDoNotAllowPads(fp)
    o=z.Outline(); o.NewOutline()
    for (x,y) in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)): o.Append(M(X0+x),M(Y0+y))
    b.Add(z)
# header pads themselves sit inside; exclude a strip around header row from footprint keepout
zone_rect(OX-2,OY+6.2,OX+35.4+2,OY+33.5+2,'OLED_KEEPOUT',[pcbnew.F_Cu],fp=True)
# silkscreen/fab outline of module
def rect(x0,y0,x1,y1,layer,w=0.12):
    s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_RECT); s.SetLayer(layer); s.SetStart(P(x0,y0)); s.SetEnd(P(x1,y1)); s.SetWidth(M(w)); b.Add(s)
rect(OX,OY,OX+35.4,OY+33.5,pcbnew.F_SilkS)
rect(OX-2,OY-2,OX+37.4,OY+35.5,pcbnew.User_1 if hasattr(pcbnew,'User_1') else pcbnew.Cmts_User,0.1)
rect(OX+2.99,OY+7.35,OX+2.99+29.42,OY+7.35+14.7,pcbnew.F_Fab,0.1)  # active area
def text(s,x,y,layer=pcbnew.F_SilkS,sz=1.0):
    t=pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x,y)); t.SetLayer(layer); t.SetTextSize(VECTOR2I(M(sz),M(sz))); t.SetTextThickness(M(0.15)); t.SetMirrored(layer==pcbnew.B_SilkS); b.Add(t)
text('1.3in SH1106 OLED (DS1) - module area, keep clear',OX+17.7,OY+31.5,pcbnew.User_1 if hasattr(pcbnew,'User_1') else pcbnew.Cmts_User,0.8)

for i,n in enumerate(['GND','VCC','CLK','MOSI','RES','DC','CS']):
    t=pcbnew.PCB_TEXT(b); t.SetText(n); t.SetPosition(P(OX+10.08+2.54*i,OY+5.0)); t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(VECTOR2I(M(0.8),M(0.8))); t.SetTextThickness(M(0.12)); t.SetTextAngleDegrees(90); b.Add(t)
# design rules / netclass RF50
ds=b.GetDesignSettings()
ds.m_MinThroughDrill=M(0.2); ds.m_TrackMinWidth=M(0.127); ds.m_HoleClearance=M(0.2); ds.SetBoardThickness(M(1.6))
# Branding (Etherkit house style, all F.SilkS) + Rev on F.Cu
def ftext(sv,x,y,layer,sz,th,ang=0):
    t=pcbnew.PCB_TEXT(b); t.SetText(sv); t.SetPosition(P(x,y)); t.SetLayer(layer); t.SetTextSize(VECTOR2I(M(sz),M(sz))); t.SetTextThickness(M(th)); t.SetTextAngleDegrees(ang); b.Add(t); return t
ftext('Si5351A VFO',64.0,57.0,pcbnew.F_SilkS,1.8,0.3)
bt=ftext('Si5351 Field Manual, Chapter 6',28.0,44.0,pcbnew.B_SilkS,1.5,0.25); bt.SetMirrored(True)
for i,x in enumerate(SMAX): ftext('CLK%d'%i,x-6.0,3.0,pcbnew.F_SilkS,1.0,0.18)
ftext('UPDI',46.8,7.4,pcbnew.F_SilkS,1.0,0.15)
for i,n in enumerate(('VCC','TXD','RXD','GND')):
    t=ftext(n,48.3,10.0+2.54*i,pcbnew.F_SilkS,0.8,0.12); t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
for (vx,vy) in LPF_VIAS:
    v=pcbnew.PCB_VIA(b); v.SetPosition(P(vx,vy)); v.SetWidth(M(0.6)); v.SetDrill(M(0.3)); v.SetNet(ni['GND']); b.Add(v)
ftext('etherkit.com 2026',64.0,59.6,pcbnew.F_SilkS,1.2,0.22)
ftext('Creative Commons License\nCC-BY-SA 4.0',64.0,62.6,pcbnew.F_SilkS,0.8,0.15)
ftext('Rev A',4.3,44.0,pcbnew.F_Cu,1.5,0.3)
for n,(x,y) in (('EtherkitLogoSmall',(84.0,61.0)),('OSHWLogo4mm',(89.3,60.6))):
    f=pcbnew.FootprintLoad(PROJ+'lib/Etherkit.pretty',n); f.SetFPID(pcbnew.LIB_ID('EtherkitKicadLibrary',n))
    f.SetReference('LOGO%d'%(1 if n[0]=='E' else 2)); f.SetBoardOnly(True); f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
    for fld in f.GetFields(): fld.SetVisible(False)
    f.SetPosition(P(x,y)); b.Add(f)
# silk cleanup: move each reference to the first candidate spot clear of pads, edges, other silk
def R2(bb): return [pcbnew.ToMM(bb.GetLeft())-X0,pcbnew.ToMM(bb.GetTop())-Y0,pcbnew.ToMM(bb.GetRight())-X0,pcbnew.ToMM(bb.GetBottom())-Y0]
obst=[]
for f in b.GetFootprints():
    for p in f.Pads():
        if p.IsOnLayer(pcbnew.F_Cu): obst.append([v+d for v,d in zip(R2(p.GetBoundingBox()),(-0.12,-0.12,0.12,0.12))])
    for g in f.GraphicalItems():
        if g.GetLayer()==pcbnew.F_SilkS and g.GetClass()!='PCB_TEXT': obst.append(R2(g.GetBoundingBox()))
for d in b.GetDrawings():
    if d.GetLayer()==pcbnew.F_SilkS: obst.append(R2(d.GetBoundingBox()))
def hit(bb,lst): return any(not(bb[2]<=o[0] or o[2]<=bb[0] or bb[3]<=o[1] or o[3]<=bb[1]) for o in lst)
ko=[OX-2,OY+6.2,OX+37.4,OY+35.5]
for d in b.GetDrawings():
    if d.GetClass()=='PCB_TEXT' and d.GetLayer()==pcbnew.F_SilkS: obst.append(R2(d.GetBoundingBox()))
for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
    t=f.Reference()
    if not t.IsVisible(): continue
    t.SetTextAngleDegrees(0)
    c=f.GetCourtyard(pcbnew.F_CrtYd); cb=R2(c.BBox()) if c.OutlineCount() else R2(f.GetBoundingBox(False))
    cx,cy=(cb[0]+cb[2])/2,(cb[1]+cb[3])/2
    cands=[(cx,cb[1]-0.6),(cx,cb[3]+0.6),(cb[0]-1.6,cy),(cb[2]+1.6,cy),(cx,cy),(cb[0]-0.2,cb[1]-0.6),(cb[2]+0.2,cb[1]-0.6),(cb[0]-0.2,cb[3]+0.6),(cb[2]+0.2,cb[3]+0.6)]
    ok=False
    cands+= [(x+dx,y) for (x,y) in cands[:4] for dx in (-1.0,1.0)]+[(cx+dx,cy+dy) for dx in (-2.5,0,2.5) for dy in (-2.2,2.2)]
    for sz in (0.8,):
        if ok: break
        t.SetTextSize(VECTOR2I(M(sz),M(sz))); t.SetTextThickness(M(min(0.12,sz*0.15)))
        for (x,y) in cands:
            t.SetPosition(P(x,y)); bb=R2(t.GetBoundingBox())
            if bb[0]<0.3 or bb[1]<0.3 or bb[2]>W-0.3 or bb[3]>H-0.3: continue
            if hit(bb,obst): continue
            ok=True; obst.append(bb); break
    if not ok:
        t.SetLayer(pcbnew.F_Fab); t.SetPosition(P(cx,cy))
# SMA launch: In1.Cu (GND plane) cut under each centre pad (pad 1.8x5.08 + 0.3 mm)
for x in SMAX: zone_rect(x-1.2,0,x+1.2,5.38,'SMA_LAUNCH_CUT_IN1',[pcbnew.In1_Cu],fp=False,tr=True,via=True,pour=True)
# --- routing constraints: fence walls crossed only on In2; In1 kept solid; In2 signal use only around the fence walls
def keep(x0,y0,x1,y1,layers,name):
    z=pcbnew.ZONE(b); z.SetIsRuleArea(True); z.SetZoneName(name)
    ls=pcbnew.LSET(); [ls.AddLayer(l) for l in layers]; z.SetLayerSet(ls)
    z.SetDoNotAllowFootprints(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(False); z.SetDoNotAllowZoneFills(False)
    o=z.Outline(); o.NewOutline()
    for (x,y) in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)): o.Append(M(X0+x),M(Y0+y))
    b.Add(z)
FB=[pcbnew.F_Cu,pcbnew.B_Cu]
keep(50.6,6.1,52.4,40.4,FB,'FENCE_WALL_L'); keep(91.6,6.1,93.4,40.4,FB,'FENCE_WALL_R'); keep(50.6,38.6,93.4,40.4,FB,'FENCE_WALL_B')
for (a,c) in ((50.6,56.0),(60.0,69.0),(73.0,82.0),(86.0,93.4)): keep(a,6.1,c,7.9,FB,'FENCE_WALL_T')
keep(0,0,100,65,[pcbnew.In1_Cu],'IN1_NO_TRACKS')
keep(OX-2,OY+4.0,OX+35.4+2,OY+33.5+2,[pcbnew.F_Cu],'OLED_NO_FCU_TRACKS')
for r in ((55,8,88,33.8),): keep(*r,[pcbnew.In2_Cu],'IN2_KEEP_SOLID_UNDER_RF')
gnd=b.FindNet('GND')
def plane(layer):
    z=pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(gnd); z.SetZoneName('GND_'+b.GetLayerName(layer))
    z.SetLocalClearance(M(0.3)); z.SetMinThickness(M(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    o=z.Outline(); o.NewOutline()
    for (x,y) in ((0,0),(W,0),(W,H),(0,H)): o.Append(M(X0+x),M(Y0+y))
    b.Add(z)
plane(pcbnew.In1_Cu); plane(pcbnew.In2_Cu)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
FABL=pcbnew.User_1 if hasattr(pcbnew,'User_1') else pcbnew.Cmts_User
for k,ln in enumerate(('FAB NOTES: JLC04161H-7628 4L 1.6mm, 1oz outer',
    'Controlled impedance 50 ohm, L1/L2, 0.31/0.20 (CPWG, RF50) per JLC calculator',
    'U3 thermal-pad vias: tented both sides + filled (epoxy)')):
    text(ln,50.0,68.0+k*1.3,FABL,0.9)
# JLC PCBA fiducials (board-only, not in BOM/schematic)
for i,(fx,fy) in enumerate(((3.0,9.0),(96.0,40.0),(4.0,52.0))):
    f=load('Fiducial:Fiducial_1mm_Mask2mm'); f.SetReference('FID%d'%(i+1)); f.SetValue('Fiducial')
    f.SetPosition(P(fx,fy)); f.SetBoardOnly(True); f.SetExcludedFromBOM(True)
    for fld in f.GetFields(): fld.SetVisible(False)
    b.Add(f)
b.Save(OUT)
print('saved',len(comps))
