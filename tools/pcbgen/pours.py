import pcbnew
PCB='/workspace/Si5351AVFO/PCB/Si5351AVFO.kicad_pcb'
b=pcbnew.LoadBoard(PCB); M=pcbnew.FromMM; gnd=b.FindNet('GND')
have={z.GetZoneName() for z in b.Zones()}
for L,cl in ((pcbnew.F_Cu,0.2),(pcbnew.B_Cu,0.25)):
    nm='GND_'+b.GetLayerName(L)
    if nm in have: continue
    z=pcbnew.ZONE(b); z.SetLayer(L); z.SetNet(gnd); z.SetZoneName(nm); z.SetAssignedPriority(0)
    z.SetLocalClearance(M(cl)); z.SetMinThickness(M(0.2)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(M(0.3)); z.SetThermalReliefSpokeWidth(M(0.4)); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    o=z.Outline(); o.NewOutline()
    for (x,y) in ((0,0),(100,0),(100,65),(0,65)): o.Append(M(100+x),M(100+y))
    b.Add(z)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(PCB); print('filled')
