import pcbnew, os
PCB='/workspace/Si5351AVFO/PCB/Si5351AVFO.kicad_pcb'; SES='/workspace/build/fr.ses'
if not os.path.exists(SES): raise SystemExit
b=pcbnew.LoadBoard(PCB)
keep=set(t.m_Uuid.AsString() for t in b.GetTracks())
pcbnew.ImportSpecctraSES(b,SES)
mode=os.environ.get('ROUTE','all')
POWER={'+5V','VBUS','+3V3D','+3V3_CLK','+3V3_OLED','/Power and USB/CP_VDD','GND'}
POWER|={n for n in b.GetNetsByName().keys() if False}
pw=lambda n: n in POWER or n.startswith(('/Power and USB/','Net-(FB','Net-(U1','Net-(U5','Net-(D1','Net-(J1'))
nadd=0
ALL=list(b.GetTracks()); kept=[]
for t in ALL:
    if t.m_Uuid.AsString() in keep: continue
    if mode=='power' and not pw(t.GetNetname()): b.Remove(t)
    else: nadd+=1; kept.append(t)
for t in kept:
    if t.GetClass()=='PCB_TRACK' and t.GetWidth()<pcbnew.FromMM(0.127): t.SetWidth(pcbnew.FromMM(0.127))
# widen +5V (USB VBUS) to 0.5 mm wherever it clears everything else by 0.17 mm
M=pcbnew.FromMM; v5=b.FindNet('+5V').GetNetCode(); others=[i for f in b.GetFootprints() for i in f.Pads()]+list(b.GetTracks()); nw=0
for t in kept:
    if t.GetClass()!='PCB_TRACK' or t.GetNetCode()!=v5: continue
    L=t.GetLayer(); s=pcbnew.SHAPE_SEGMENT(t.GetStart(),t.GetEnd(),M(0.5))
    if all(not(o.GetNetCode()!=v5 and o.IsOnLayer(L) and o.GetEffectiveShape(L).Collide(s,M(0.17))) for o in others):
        t.SetWidth(M(0.5)); nw+=1
print('+5V widened',nw)
b.Save(PCB); print('imported',nadd,'mode',mode)
