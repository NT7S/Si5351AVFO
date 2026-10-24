import cadquery as cq
D='/workspace/Si5351AVFO/PCB/lib/Etherkit.3dshapes/'
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane().box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
def cyl(x,y,z0,z1,d): return cq.Workplane().circle(d/2).extrude(z1-z0).translate((x,y,z0))
def save(s,n): cq.exporters.export(s,D+n+'.step')
# EC11E vertical H20, origin pin A, shaft (7.5,-2.5)
e=box(1.65,13.35,-8.5,3.5,0,6.5).union(cyl(7.5,-2.5,6.5,13,7)).union(cyl(7.5,-2.5,13,20,6))
save(e,'EC11E_Vertical_H20_simple')
save(box(-2.55,2.55,-2.55,2.55,0,1.2).union(cyl(0,0,1.2,1.5,2.6)),'TS-1187A_simple')
save(box(-4.47,4.47,-4.15,3.2,0,3.26),'USB_C_HCTL_HC-TYPE-C-16P-01A_simple')
save(box(-1.6,1.6,-1.25,1.25,0,1.0),'Osc_3.2x2.5_simple')
# SMA end launch: flange at edge (fp y 0 => model y 0), body outside board (model -y = fp +y)
s=box(-3.2,3.2,-1.6,0,-3.2,3.2).union(cq.Workplane('XZ').circle(3.1).extrude(8).translate((0,-1.6,0))).union(box(-0.25,0.25,0,4.5,0,0.2))
save(s,'SMA_EndLaunch_simple')
# OLED module on 7-pin header (DS1 rot 90 frame)
m=box(-31.5,2.0,-25.32,10.08,2.5,3.7).union(box(-26.25,-3.25,-24.82,9.58,3.7,5.2))
for i in range(7): m=m.union(box(-0.32,0.32,-0.32-2.54*i,0.32-2.54*i,-3,6.5)).union(box(-1.27,1.27,-1.27-2.54*i,1.27-2.54*i,0,2.5))
save(m,'OLED_1.3in_SH1106_on_header_simple')
save(box(-3,3,-3,3,0,3.5).union(box(-4.3,4.3,-2.6,-1.9,0,0.3)).union(box(-4.3,4.3,1.9,2.6,0,0.3)).union(cyl(0,0,3.5,11.0,3.5)),'SW_6x6_H11_simple')
# SH1 RF fence (DNP, user-cut tin can): open-top 0.25 mm wall, 3 mm tall, centred on the 1 mm GND strip; fp origin = top-left corner, model y = -fp y
W,H,T,c=42.0,33.5,0.25,0.5
fence=box(c-T/2,W-c+T/2,-c-T/2,-c+T/2,0,3).union(box(c-T/2,W-c+T/2,-(H-c)-T/2,-(H-c)+T/2,0,3)).union(box(c-T/2,c+T/2,-(H-c),-c,0,3)).union(box(W-c-T/2,W-c+T/2,-(H-c),-c,0,3))
save(fence,'RF_Fence_42x33.5_can_simple')
