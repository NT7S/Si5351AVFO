import sys,copy
from build import *
from sexp import parse
REVF=parse(open('/workspace/aprev/repo/pcb/Si5351ABreakout.kicad_sch').read())
REVF_LIBS=find(REVF,'lib_symbols')[0]
R0805='Resistor_SMD:R_0805_2012Metric'; R0603='Resistor_SMD:R_0603_1608Metric'
C0805='Capacitor_SMD:C_0805_2012Metric'; C0603='Capacitor_SMD:C_0603_1608Metric'; C1206='Capacitor_SMD:C_1206_3216Metric'
L0805='Inductor_SMD:L_0805_2012Metric'; FB0603='Inductor_SMD:L_0603_1608Metric'
def LC(lcsc,mpn=None,mfr=None):
    d={'LCSC':lcsc}
    if mpn: d['MPN']=mpn
    if mfr: d['Manufacturer']=mfr
    return d
C100N=LC('C49678','CC0805KRX7R9BB104','YAGEO'); C4U7=LC('C1779','CL21A475KAQNNNE','Samsung'); C1U=LC('C28323','CL21B105KBFNNNE','Samsung')
R10K=LC('C17414','0805W8F1002T5E','UNI-ROYAL'); R0R=LC('C17477','0805W8F0000T5E','UNI-ROYAL')
def R(s,ref,val,x,y,n1,n2,r=0,fp=R0805,fields=None,dnp=False,vfy=None,lib=('Device','R_Small'),fieldpos=None):
    fpos=fieldpos or ({'Reference':(1.8,-0.6),'Value':(1.8,1.6)} if r==0 else {'Reference':(0,-2.54),'Value':(0,2.54)})
    return s.place(lib[0],lib[1],ref,val,x,y,{'1':n1,'2':n2},r=r,fp=fp,fields=fields,dnp=dnp,vfy=vfy,fieldpos=fpos)
def C(s,*a,**k): k.setdefault('fp',C0805); k['lib']=('Device','C_Small'); return R(s,*a,**k)
def L(s,*a,**k): k.setdefault('fp',L0805); k['lib']=('Device','L_Small'); return R(s,*a,**k)
def FB(s,*a,**k): k.setdefault('fp',FB0603); k['lib']=('Device','FerriteBead_Small'); return R(s,*a,**k)

sheets=[]
def flagrail(s,net,x,y):
    s.power(net,x,y,'down' if net=='GND' else 'up'); s.wire([(g_(x),g_(y)),(g_(x+12.7),g_(y))]); s.flag(x+12.7,y)
from build import g as g_
# ================= POWER / USB =================
P=Sheet('power_usb.kicad_sch','Power and USB','b0000000-0000-4000-8000-000000000002',2); sheets.append(P)
P.text('USB-C input, CP2102N USB-UART (from EtherkitUARTAdapter), LP2985 rails (U1 from Rev F; U5 dedicated to OLED per Jason 2026-10-22)',20,20,2)
P.place('Connector','USB_C_Receptacle_USB2.0_16P','J1','USB_C_Receptacle',45,80,
  {'A4':'+5V','A5':'WIRE','B5':'WIRE','A6':'USB_DP','B6':'USB_DP','A7':'USB_DM','B7':'USB_DM','A8':'NC','B8':'NC','A1':'GND','SH':'GND'},
  fp='Connector_USB:USB_C_Receptacle_HCTL_HC-TYPE-C-16P-01A',fields=LC('C2894897','HC-TYPE-C-16P-01A','HCTL'),
  vfy='UART adapter schematic pairs GCT USB4105 footprint with this HCTL LCSC part; HCTL footprint used here - confirm. Shield to GND assumed (not stated in PLAN).')
R(P,'R1','5.1k',92.71,100,'WIRE','GND',fp=R0603,fields=LC('C105580','RC0603FR-075K1L','YAGEO'))
R(P,'R2','5.1k',80.01,100,'WIRE','GND',fp=R0603,fields=LC('C105580','RC0603FR-075K1L','YAGEO'))
P.place('Power_Protection','SP0503BAHT','D1','SP0503BAHT',110,125,{'1':'GND','2':'USB_DM','3':'USB_DP','4':('+5V',5.08)},fields=LC('C7074','SP0503BAHTG','Littelfuse'),fieldpos={'Reference':(5.08,-1.27),'Value':(10.16,1.27)},
  vfy='Pin-to-line mapping (D-/D+/VBUS on pins 2/3/4) to be checked against adapter layout.')
a5=P.pinpos[('J1','A5')]; b5=P.pinpos[('J1','B5')]
P.wire([a5,(92.71,a5[1]),P.pinpos[('R1','1')]]); P.wire([b5,(80.01,b5[1]),P.pinpos[('R2','1')]])
C(P,'C10','100n',125,120,'+5V','GND',fp=C0603,fields=LC('C14663','CC0603KRX7R9BB104','YAGEO'),vfy='LCSC stock low; fallback C49678 (0805) per PLAN')
C(P,'C11','4.7u',137.16,120,'+5V','GND',fp=C0603,fields=LC('C1705','CL10A475KP8NNNC','Samsung'))
P.place('Interface_USB','CP2102N-Axx-xQFN24','U3','CP2102N-A02-GQFN24',190,85,
  {'3':'USB_DP','4':'USB_DM','8':'CP_VBUS_SENSE','9':'CP_RST','5':'WIRE','6':('CP_VDD',2.54),'7':('+5V',7.62),'2':'GND',
   '21':'MCU_RX','20':'MCU_TX','23':'DTR','14':'NC','13':'NC'},
  fields=LC('C969151','CP2102N-A02-GQFN24R','Silicon Labs'),vfy='Unused CP2102N pins left NC (adapter used DTR via JP1, TRRS dropped). Confirm none were strapped on the adapter.')
x5,y5=P.pinpos[('U3','5')]; x6,y6=P.pinpos[('U3','6')]; P.wire([(x5,y5),(x5,y5-2.54),(x6,y6-2.54)])
R(P,'R7','22.1k',150,60,'+5V','CP_VBUS_SENSE',fp=R0603,fields=LC('C137768','RC0603FR-0722K1L','YAGEO'))
R(P,'R8','47.5k',150,80,'WIRE','GND',fp=R0603,fields=LC('C2933225','FRC0603F4752TS','FOJAN'))
P.wire([P.pinpos[('R7','2')],P.pinpos[('R8','1')]])
R(P,'R9','1k',137.16,60,'+5V','CP_RST',fp=R0603,fields=LC('C110776','RT0603BRD071KL','YAGEO'),vfy='PLAN says /RST pull-up to VBUS (as on adapter); CP2102N RST max is VIO-referenced - confirm adapter really ties to VBUS.')
C(P,'C12','4.7u',220,50,'CP_VDD','GND',fp=C0603,fields=LC('C1705','CL10A475KP8NNNC','Samsung'))
C(P,'C13','100n',232.41,50,'CP_VDD','GND',fp=C0603,fields=LC('C14663','CC0603KRX7R9BB104','YAGEO'))
P.flag(245.11,45); P.label('CP_VDD',245.11,45,0)
# LDOs
def ldo(ref,X,Y,out,cin,cbp,cout):
    P.place('Regulator_Linear','LP2985-3.3',ref,'LP2985-3.3',X,Y,{'1':('+5V',7.62),'3':'WIRE','4':'WIRE','5':'WIRE' if not out.startswith('+') else (out,7.62),'2':'GND'},
      fields=LC('C16085','LP2985AIM5-3.3/NOPB','TI'),fieldpos={'Reference':(-5.08,-6.6),'Value':(7.62,6.35)})
    a=P.pinpos[(ref,'1')]; b=P.pinpos[(ref,'3')]; P.wire([b,a])
    C(P,cin,'1u',X-30,Y+17.78,'+5V','GND',fields=C1U)
    C(P,cbp,'100n',X+20,Y+17.78,'WIRE','GND',fields=C100N)
    C(P,cout,'4.7u',X+35,Y+17.78,'WIRE' if not out.startswith('+') else out,'GND',fields=C4U7)
    bp=P.pinpos[(ref,'4')]; c=P.pinpos[(cbp,'1')]; P.wire([bp,(c[0],bp[1]),c])
P.text('U1: +3V3D (MCU) and, via FB1, +3V3_CLK (Si5351 + TCXO). Rev F U1/C1/C2/C3.',30,150)
ldo('U1',70,170,'+3V3D','C1','C2','C3')
FB(P,'FB1','BLM18PG221',140,185,('+3V3D',7.62),('+3V3_CLK',7.62),r=90,fields=LC('C80165','BLM18PG221SN1D','Murata'))
flagrail(P,'+3V3_CLK',160,178)
P.text('U5: OLED-only rail (Eyes On The Prize lesson, PLAN 4a). Place U5/FB2/C22-C24 at the OLED header.',30,215)
ldo('U5',70,235,'OLED_LDO_OUT','C7','C8','C9')
FB(P,'FB2','BLM18PG221',142.24,232.41,'WIRE',('+3V3_OLED',7.62),r=90,fields=LC('C80165','BLM18PG221SN1D','Murata'),
   vfy='Bead or series R (<=6 ohm upper bound, PLAN 4a); value to be set by measurement.')
o=P.pinpos[('U5','5')]; c9=P.pinpos[('C9','1')]; fb=P.pinpos[('FB2','1')]
P.wire([o,fb]); P.wire([(c9[0],o[1]),c9])
C(P,'C22','4.7u',160,262,'+3V3_OLED','GND',fields=C4U7,vfy='OLED bulk value: PLAN start point 2x4.7u, tune by measurement')
C(P,'C23','4.7u',172.72,262,'+3V3_OLED','GND',fields=C4U7)
C(P,'C24','DNP',185.42,262,'+3V3_OLED','GND',fp=C1206,dnp=True,vfy='DNP 1206 site for larger OLED bulk cap; value/part not chosen')
flagrail(P,'+3V3_OLED',200,245)
flagrail(P,'+5V',30,45); flagrail(P,'GND',30,55)
for i,(x,y) in enumerate([(320,60),(335,60),(350,60),(365,60)]):
    P.place('Mechanical','MountingHole','H%d'%(i+1),'M3',x,y,{},fp='MountingHole:MountingHole_3.2mm_M3')
# ================= MCU / UI =================
M=Sheet('mcu_ui.kicad_sch','MCU and UI','b0000000-0000-4000-8000-000000000003',3); sheets.append(M)
M.text('ATtiny3226 @ 8 MHz internal, 3.3 V. Optiboot over CP2102N; DTR auto-reset on PB4 (RSTPINCFG=0x3, megaTinyCore "UPDI w/reset on PB4"), as EtherKeyerMini C3/R4.',20,20,2)
M.place('MCU_Microchip_ATtiny','ATtiny3226-S','U4','ATtiny3226-SU',150,110,
 {'1':'+3V3D','20':'GND','16':'UPDI_PA0','17':'OLED_MOSI','18':'OLED_FS0','19':'OLED_SCK','2':'OLED_CS1','3':'OLED_DC','4':'OLED_CS2','5':'BTN_MENU',
  '11':'I2C_SCL','10':'I2C_SDA','9':'MCU_TX','8':'MCU_RX','7':'WIRE','6':'BTN_STEP','12':'ENC_A','13':'ENC_B','14':'ENC_SW','15':'BTN_BAND'},
 fields=LC('C3234898','ATTINY3226-SU','Microchip'),vfy='Pin mux (PLAN sec.3) to be checked vs datasheet I/O mux table. Jason consigning parts.')
C(M,'C15','100n',120,70,'+3V3D','GND',fields=C100N); C(M,'C16','4.7u',132.08,70,'+3V3D','GND',fields=C4U7)
C(M,'C14','100n',185.42,134.62,'DTR','WIRE',r=180,fields=C100N,fieldpos={'Reference':(4.45,-1.27),'Value':(4.45,1.27)},vfy='PLAN: series R or clamp on PB4 for DTR-rising overshoot? EKM has none.')
R(M,'R12','10k',185.42,116.84,'+3V3D','WIRE',fields=R10K)
r7=M.pinpos[('U4','7')]; M.wire([r7,(185.42,r7[1])]); M.wire([M.pinpos[('R12','2')],M.pinpos[('C14','2')]])
# UPDI: replicated exactly from EtherKeyerMini PCB/EtherKeyerMini.kicad_sch (J3,R3,D1,D2,JP2,JP3)
EKMV='Replicated from EtherKeyerMini (%s); EKM has no LCSC/MPN fields - part number to choose.'
M.text('UPDI / serial-UPDI header, circuit copied from EtherKeyerMini (J3,R3,D1 -> J5,R13,D4;\nEKM D2/JP2/JP3 omitted per Jason). Pin 1 VCC ref (+3V3D), 2 TXD, 3 RXD/UPDI, 4 GND.',262,140)
M.place('Connector_Generic','Conn_01x04','J5','UPDI',334,170.18,{'1':'WIRE','2':'WIRE','3':'WIRE','4':'WIRE'},
  fp='Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical',vfy=EKMV%'J3')
p1,p2,p3,p4=[M.pinpos[('J5',n)] for n in '1234']
M.wire([p4,(p4[0]-2.54,p4[1])]); M.power('GND',p4[0]-2.54,p4[1],'left')
M.wire([p2,(p2[0]-2.54,p2[1])]); M.label('UPDI_TXD',p2[0]-2.54,p2[1],180)
M.wire([p1,(p1[0]-5.08,p1[1])]); M.power('+3V3D',p1[0]-5.08,p1[1],'up')
M.text('Pin 1 = VCC reference for programmer; board must be USB-powered while programming.',262,158)
R(M,'R13','470',270.51,177.8,'UPDI_PA0','WIRE',r=90,fp='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical',vfy=EKMV%'R3')
r2=M.pinpos[('R13','2')]
M.wire([r2,(p3[0]-7.62,r2[1]),(p3[0]-7.62,p3[1]),p3])
jx=309.88
M.place('Device','D_Schottky','D4','1N5711',jx,185.42,{'1':'WIRE','2':'WIRE'},r=90,fp='Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal',vfy=EKMV%'D1',
  fieldpos={'Reference':(5.08,-1.27),'Value':(7.62,1.27)})
dA=M.pinpos[('D4','2')]; dK=M.pinpos[('D4','1')]
top,bot=(dA,dK) if dA[1]<dK[1] else (dK,dA)
M.wire([(jx,r2[1]),top]); M.wire([bot,(jx,bot[1]+2.54),(jx+5.08,bot[1]+2.54)]); M.label('UPDI_TXD',jx+5.08,bot[1]+2.54,0)
M.junction(jx,r2[1])
M.place('Connector_Generic','Conn_01x08','DS1','HS13L01W4S01',300,100,
 {'1':'WIRE','2':('+3V3_OLED',17.78),'3':'OLED_SCK','4':'OLED_MOSI','5':'OLED_DC','6':'OLED_CS1','7':'OLED_FS0','8':'OLED_CS2'},
 fp='Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical',fields=LC('C5139764','HS13L01W4S01','HS'),
 vfy='1.3in SPI SH1106 module. Pin order GND,VCC,SCL,SDA,DC,CS1,FS0,CS2 from PLAN pin list; pin numbering, pitch and connector style unverified. Low stock - Jason sourcing.')
d1=M.pinpos[('DS1','1')]; M.wire([d1,(d1[0]-2.54,d1[1])]); M.power('GND',d1[0]-2.54,d1[1],'left')
R(M,'R26','10k',270,70,'+3V3D','OLED_CS2',fields=R10K)
M.text('OLED: SPI only (PA1 MOSI, PA3 SCK, PA4 CS1, PA5 DC). Never shares the Si5351 I2C bus.\nCS2 (font chip) held high by R26.',255,130)
# debounce: switch node pulled up, 10k series to pin, 100n at pin
chans=[('ENC_A','R14','R21','C17'),('ENC_B','R15','R22','C18'),('ENC_SW','R16','R23','C19'),('BTN_BAND','R17','R24','C20'),('BTN_STEP','R18','R25','C21'),('BTN_MENU','R19','R20','C25')]
for i,(n,rs,rp,cc) in enumerate(chans):
    x=25+i*42; y=215
    R(M,rp,'10k',x,y-12.7,'+3V3D','WIRE',fields=R10K)
    R(M,rs,'10k',x+7.62,y,'WIRE','WIRE',r=90,fields=R10K)
    C(M,cc,'100n',x+15.24,y+7.62,'WIRE','GND',fields=C100N,vfy='Debounce topology/count: PLAN lists x5 but 6 inputs (A,B,SW,3 buttons) - drawn as 6. Check vs encoder bounce spec.' if i==0 else None)
    pu=M.pinpos[(rp,'2')]; s1=M.pinpos[(rs,'1')]; s2=M.pinpos[(rs,'2')]; c1=M.pinpos[(cc,'1')]
    M.wire([pu,(pu[0],s1[1]),s1]); M.wire([s2,(c1[0],s2[1]),c1])
    M.label(n+'_SW',pu[0],s1[1],180); M.label(n,c1[0],s2[1],0)
M.place('Device','RotaryEncoder_Switch','SW1','EC11E18244A5',50,260,{'A':'ENC_A_SW','B':'ENC_B_SW','C':('GND',15.24),'S1':'ENC_SW_SW','S2':'GND'},
  fp='Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm',fields=LC('C255515','EC11E18244A5','ALPS Alpine'),vfy='Detent/pulse count unverified.')
for i,(ref,n,nm) in enumerate([('SW2','BTN_BAND_SW','BAND'),('SW3','BTN_STEP_SW','STEP'),('SW4','BTN_MENU_SW','MENU')]):
    M.place('Switch','SW_Push',ref,nm,110+i*30,260,{'1':n,'2':'GND'},fp='Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A',fields=LC('C318884','TS-1187A-B-A-B','XKB'))
# ================= SYNTH / RF =================
S=Sheet('synth_rf.kicad_sch','Synth and RF outputs','b0000000-0000-4000-8000-000000000004',4); sheets.append(S)
S.text('Si5351A + 25 MHz TCXO copied from Si5351A Breakout Rev F (R5/C5/C6/R6/C4, XB open). Each output: Rs 0R -> Cb 100n DC block -> DNP shunt -> LPF (DNP) with 0R bypass -> SMA.',20,20,2)
S.place('Si5351ABreakout','TCXO_4P','X1','25MHz TCXO',59.69,87.63,{'1':'WIRE','2':'GND','3':'WIRE','4':'WIRE'},src=REVF_LIBS,libname='Si5351AVFO',
  fields=LC('C48888230','OW2EL89CENUXK7YLC-25M','YXC'),vfy='TCXO stock thin (718); buy before ordering.')
R(S,'R5','10',59.69,67.31,'+3V3_CLK','WIRE',fields=LC('C17415','0805W8F100JT5E','UNI-ROYAL'))
C(S,'C5','100n',85.09,74.93,'WIRE','GND',fields=C100N)
S.flag(85.09,72.39)
R(S,'R6','0',44.45,74.93,'WIRE','WIRE',fields=R0R,dnp=True)
C(S,'C6','100n',80.01,87.63,'WIRE','WIRE',r=90,fields=C100N)
S.place('Oscillator','Si5351A-B-GT','U2','Si5351A-B-GT',140,95,{'1':('+3V3_CLK',2.54),'7':'WIRE','2':'WIRE','3':'NC','4':'I2C_SCL','5':'I2C_SDA','8':'GND','10':'CLK0','9':'CLK1','6':'CLK2'},
  fields=LC('C504891','SI5351A-B-GTR','Skyworks/Silicon Labs'))
a=S.pinpos[('U2','1')]; b=S.pinpos[('U2','7')]; S.wire([b,(b[0],b[1]-2.54),(a[0],a[1]-2.54)])
S.wire([S.pinpos[('R5','2')],S.pinpos[('X1','4')]]); S.wire([(59.69,72.39),(85.09,72.39)]); S.wire([(59.69,72.39),(44.45,72.39)])
r6=S.pinpos[('R6','2')]; x1=S.pinpos[('X1','1')]; S.wire([r6,(r6[0],x1[1]),x1])
S.wire([S.pinpos[('X1','3')],S.pinpos[('C6','1')]]); S.wire([S.pinpos[('C6','2')],S.pinpos[('U2','2')]])
C(S,'C4','100n',165,60,'+3V3_CLK','GND',fields=C100N)
R(S,'R27','VERIFY 2.2k-4.7k',100,130,'+3V3D','I2C_SCL',vfy='I2C pull-up value not fixed (PLAN 2.2-4.7k); no LCSC chosen. On +3V3D: ATtiny, Si5351, CP2102N and OLED all at 3.3 V, so I2C levels match.')
R(S,'R28','VERIFY 2.2k-4.7k',140,130,'+3V3D','I2C_SDA',vfy='as R27')
for k in range(3):
    y=172.72+k*45.72
    n='CLK%d'%k; rb=100+k*20; cb=100+k*20; lb=1+k*3
    S.text('%s output chain (J%d)'%(n,k+2),20,y-24)
    R(S,'R%d'%rb,'0',40.64,y,n,'WIRE',r=90,fp=R0603,fields={'LCSC':''},vfy='0603 0R series (Jason decision); LCSC code not in PLAN (C17477 is 0805).' if k==0 else 'see R100')
    C(S,'C%d'%cb,'100n',50.8,y,'WIRE','WIRE',r=90,fields=C100N,vfy='DC-block LF corner ~32 kHz into 50 ohm (PLAN Q6).' if k==0 else None)
    S.wire([S.pinpos[('R%d'%rb,'2')],S.pinpos[('C%d'%cb,'1')]])
    R(S,'R%d'%(rb+1),'120',60.96,y+5.08,'WIRE','GND',dnp=True,vfy='DNP shunt ~120 ohm back-match of ~85 ohm source (datasheet Zo); part/LCSC not chosen; verify return loss esp. >100 MHz.' if k==0 else 'see R100')
    R(S,'R%d'%(rb+2),'0',101.6,y,'WIRE','WIRE',r=90,fields=R0R,dnp=True)  # RA
    S.wire([S.pinpos[('C%d'%cb,'2')],S.pinpos[('R%d'%(rb+2),'1')]]); S.wire([(60.96,y),S.pinpos[('R%d'%(rb+1),'1')]])
    xs=[121.92+j*22.86 for j in range(3)]
    for j in range(3):
        L(S,'L%d'%(lb+j),'DNP',xs[j],y,'WIRE','WIRE',r=90,dnp=True,vfy='LPF inductor size (SMD vs T37 option, PLAN Q7)' if (k==0 and j==0) else None)
        C(S,'C%d'%(cb+5+j),'DNP',xs[j],y-7.62,'WIRE','WIRE',r=90,dnp=True,vfy='Parallel C across L (elliptic) per LowPassFilterModule - unconfirmed' if (k==0 and j==0) else None)
        l1=S.pinpos[('L%d'%(lb+j),'1')]; l2=S.pinpos[('L%d'%(lb+j),'2')]
        S.wire([l1,S.pinpos[('C%d'%(cb+5+j),'1')]]); S.wire([l2,S.pinpos[('C%d'%(cb+5+j),'2')]])
    shx=[109.22]+[x+7.62 for x in xs]
    for j in range(4):
        C(S,'C%d'%(cb+1+j),'DNP',shx[j],y+5.08,'WIRE','GND',dnp=True,vfy='LPF values builder choice (DNP)' if (k==0 and j==0) else None)
        S.wire([(shx[j],y),S.pinpos[('C%d'%(cb+1+j),'1')]])
    R(S,'R%d'%(rb+3),'0',185.42,y,'WIRE','WIRE',r=90,fields=R0R,dnp=True)  # RB
    S.place('Connector','Conn_Coaxial','J%d'%(k+2),'SMA '+n,203.2,y,{'1':'WIRE','2':'GND'},fp='Connector_Coaxial:SMA_Samtec_SMA-J-P-H-ST-EM1_EdgeMount',
      fields=LC('C496550','BWSMA-KE-P001','BAT Wireless'),vfy='Footprint is a placeholder; check BWSMA-KE-P001 launch geometry and 1.6 mm edge fit.' if k==0 else 'see J2')
    chainpts=[S.pinpos[('R%d'%(rb+2),'2')]]
    for j in range(3): chainpts+= [S.pinpos[('L%d'%(lb+j),'1')],S.pinpos[('L%d'%(lb+j),'2')]]
    chainpts+=[S.pinpos[('R%d'%(rb+3),'1')]]
    for a_,b_ in zip(chainpts[0::2],chainpts[1::2]): S.wire([a_,b_])
    S.wire([S.pinpos[('R%d'%(rb+3),'2')],S.pinpos[('J%d'%(k+2),'1')]])
    R(S,'R%d'%(rb+4),'0',88.9,y+20.32,'WIRE','WIRE',r=90,fields=R0R)          # RC bypass fitted
    S.wire([(76.2,y),(76.2,y+20.32),S.pinpos[('R%d'%(rb+4),'1')]])
    S.wire([S.pinpos[('R%d'%(rb+4),'2')],(193.04,y+20.32),(193.04,y)])
S.text('Bypass: RC (R104/R124/R144) fitted by default; RA/RB DNP. Filter build: fit RA/RB, remove RC.\nKeep RA/RB pads <=2 mm from junction (PLAN 6).',200,100)
# ================= VERIFY text blocks + root =================
P.vpos=(230,150); M.vpos=(195,238); S.vpos=(290,40)
for sh in sheets:
    import textwrap
    sh.text('VERIFY (unconfirmed items on this sheet):\n'+'\n'.join('\n'.join(textwrap.wrap('- '+v,120,subsequent_indent='   ')) for v in sh.verify),*sh.vpos,1.0)
    VERIFY_ALL.extend(sh.verify)
    sh.save()
root=Sheet('Si5351AVFO.kicad_sch','Top','',1)
root.text('Si5351A VFO Rev A - Field Manual Ch. 6. Plan: PLAN.md (2026-10-22). Hierarchy: power/USB, MCU/UI, synth/RF.\nInter-sheet nets via global labels (MCU_TX, MCU_RX, DTR, I2C_SCL, I2C_SDA) and power rails.',20,20,2)
extra=[]
for i,sh in enumerate(sheets):
    x,y,w,h=40+i*90,60,70,30
    extra.append(['sheet',['at',f(x),f(y)],['size',f(w),f(h)],['exclude_from_sim','no'],['in_bom','yes'],['on_board','yes'],['dnp','no'],['fields_autoplaced','yes'],
      ['stroke',['width','0.1524'],['type','solid']],['fill',['color','0','0','0','0.0000']],['uuid',q(sh.su)],
      ['property','"Sheetname"',q(sh.title),['at',f(x),f(y-0.7),'0'],['effects',['font',['size','1.27','1.27']],['justify','left','bottom']]],
      ['property','"Sheetfile"',q(sh.fname),['at',f(x),f(y+h+0.6),'0'],['effects',['font',['size','1.27','1.27']],['justify','left','top']]],
      ['instances',['project',q(PROJ),['path',q('/'+ROOT_UUID),['page',q(str(sh.page))]]]]])
extra.append(['sheet_instances',['path','"/"',['page','"1"']]])
root.uuid=ROOT_UUID
root.save(extra)
open('verify.txt','w').write('\n'.join(VERIFY_ALL)+'\n')

# project library with the Rev F TCXO symbol
tc=copy.deepcopy(S.libs['Si5351AVFO:TCXO_4P']); tc[1]='"TCXO_4P"'
open('Si5351AVFO.kicad_sym','w').write(dump(['kicad_symbol_lib',['version','20241209'],['generator','"kicad_symbol_editor"'],['generator_version','"10.0"'],tc])+'\n')
open('sym-lib-table','w').write('(sym_lib_table\n\t(version 7)\n\t(lib (name "Si5351AVFO") (type "KiCad") (uri "${KIPRJMOD}/Si5351AVFO.kicad_sym") (options "") (descr "Project symbols (TCXO_4P from Si5351A Breakout Rev F)"))\n)\n')
