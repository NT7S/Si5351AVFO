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
b.Save(PCB); print('imported',nadd,'mode',mode)
