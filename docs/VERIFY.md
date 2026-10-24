# VERIFY checklist - Si5351AVFO Rev A

Tick a box when an item is closed. Write replies on the `Jason:` line under each item.
Checked items are finalized and their notes have been removed from the schematic; open items still appear in each sheet's VERIFY note.

- [x] **J1**: UART adapter schematic pairs GCT USB4105 footprint with this HCTL LCSC part; HCTL footprint used here - confirm. Shield to GND assumed (not stated in PLAN).
  - Jason: OK

- [x] **D1**: Pin-to-line mapping (D-/D+/VBUS on pins 2/3/4) to be checked against adapter layout.
  - Jason: OK

- [x] **C10**: LCSC stock low; fallback C49678 (0805) per PLAN
  - Jason: ACKNOWLEDGED

- [x] **U3**: Unused CP2102N pins left NC (adapter used DTR via JP1, TRRS dropped). Confirm none were strapped on the adapter.
  - Jason: OK

- [x] **R9**: PLAN says /RST pull-up to VBUS (as on adapter); CP2102N RST max is VIO-referenced - confirm adapter really ties to VBUS.
  - Jason: INVESTIGATE FURTHER
  - KiCad EE: Moved R9's top from +5V to CP_VDD (VIO/VDD, pins 5/6); still 1k, C110776. The data sheet recommends a 1k RSTb pull-up tied to VIO (CP2102N data sheet rev 1.5 (Silicon Labs) §2.1). RSTb's abs max is VIO+2.5 V when VIO < 3.3 V (Table 3.10), and the internal regulator can sit at 3.1 V (Table 3.6), so 5 V on RSTb can exceed the rating. The adapter's VBUS pull-up is outside spec; it just happened to work.

- [x] **FB2**: Bead or series R (<=6 ohm upper bound, PLAN 4a); value to be set by measurement.
  - Jason: OK

- [x] **C22**: OLED bulk value: PLAN start point 2x4.7u, tune by measurement
  - Jason: INVESTIGATE FURTHER
  - KiCad EE: Kept 2× 4.7u 0805 X5R 25 V (C22/C23, C1779, 2.06 M in stock). The module draws 45 mA typ / 50 mA max from its internal DC/DC (HS13L01 data sheet, IBAT). LP2985 allows up to 200 µF on its output, assuming 50% derating (LP2985 data sheet, Recommended Operating Conditions), so the bulk adds no stability risk. Final tuning still needs measuring with the radio running, as PLAN §4a says.

- [x] **C24**: DNP 1206 site for larger OLED bulk cap; value/part not chosen
  - Jason: INVESTIGATE FURTHER
  - KiCad EE: Fitted C24: 22u 1206 X5R 25 V, Samsung CL31A226KAHNNNE, C12891, 1.63 M in stock. Reasoning: in your 'Eyes On The Prize' rig, a series R plus large bulk on OLED VCC cured the hum. With the ≤6 Ω R_OLED upper bound (PLAN §4a), 2×4.7u (~6 µF after DC bias) gives a corner of ~4.4 kHz, inside the audio band. Adding 22u (~15 µF effective) moves it to about 1.3 kHz. Total stays far under LP2985's 200 µF max. If the cap turns out to be unneeded, it can be marked DNP later.

- [x] **U4**: Pin mux (PLAN sec.3) to be checked vs datasheet I/O mux table. Jason consigning parts.
  - Jason: EVERYTHING OK BUT DOUBLE-CHECK UART PINS
  - KiCad EE: UART pins checked and correct. CP2102N QFN24 pin 21 TXD (output) → MCU_RX → U4 pin 8 PB3 = USART0 RxD. U4 pin 9 PB2 = USART0 TxD → MCU_TX → CP2102N pin 20 RXD (input). Both are default (non-PORTMUX) USART0 pins. DTR is pin 23 → C14 → PB4 (pin 7, alternate RESET). Sources: CP2102N data sheet rev 1.5 (Silicon Labs) Table 5.2; ATtiny3224/3226/3227 data sheet DS40002345B (Microchip) §2.2 20-pin SOIC pinout and Table 3-1.

- [x] **C14**: PLAN: series R or clamp on PB4 for DTR-rising overshoot? EKM has none.
  - Jason: INVESTIGATE FURTHER
  - KiCad EE: Added R29 1k 0603 (UNI-ROYAL 0603WAF1001T5E, C21190, 35 M in stock) in series between C14 and PB4. The PB4 node sits at 3.3 V through R12. When DTR rises (0→3.3 V), the node is AC-coupled to ~6.6 V. The pin's abs max is VDD+0.5 V and injection current is ±15 mA max (ATtiny3224/3226/3227 data sheet DS40002345B (Microchip) Table 33-1, note 1: a current-limiting resistor is required above VDD+0.6 V). Without R29, only the CP2102N's driver (~100 Ω) limits the current, which gives roughly 27 mA. With R29: (6.6−3.9)/1k ≈ 2.7 mA. When DTR falls, PB4 drops to 3.3×1k/11k ≈ 0.3 V, below RESET VIL. The pulse time constant is 100n×11k ≈ 1.1 ms, far longer than the 2.5 µs minimum RESET pulse (ATtiny3224/3226/3227 data sheet DS40002345B (Microchip) tMIN_RST). Netlist change: C14 pin 2 now goes through R29 to the PB4 node.

- [x] **J5**: Replicated from EtherKeyerMini (J3); EKM has no LCSC/MPN fields - part number to choose.
  - Jason: 0.1" HEADER
  - KiCad EE: Footprint is now Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical (it was a pin socket). Part: Ckmtw B-2100S04P-A110, 1x4 2.54 mm male header, C124378, 61 k in stock.

- [x] **R13**: Replicated from EtherKeyerMini (R3); EKM has no LCSC/MPN fields - part number to choose.
  - Jason: YOU CHOOSE
  - KiCad EE: 470R in 0603 SMD (was THT axial): UNI-ROYAL 0603WAF4700T5E, C23179, a basic part with 5.1 M in stock. Same value as EKM R3.

- [x] **D4**: Replicated from EtherKeyerMini (D1); EKM has no LCSC/MPN fields - part number to choose.
  - Jason: YOU CHOOSE A SUITABLE SMT REPLACEMENT
  - KiCad EE: 1N5711W-7-F, Diodes Inc, SOD-123, C154843, 10.6 k in stock. Footprint Diode_SMD:D_SOD-123. It's the same 1N5711 Schottky (70 V, 15 mA) in SMD, so the SerialUPDI behavior is unchanged. Pin 1 K is on UPDI_TXD and pin 2 A is on the UPDI node, as before.

- [x] **DS1**: 1.3in SPI SH1106 module. Pin order GND,VCC,SCL,SDA,DC,CS1,FS0,CS2 from PLAN pin list; pin numbering, pitch and connector style unverified. Low stock - Jason sourcing.
  - Jason: OK

- [x] **C17**: Debounce topology/count: PLAN lists x5 but 6 inputs (A,B,SW,3 buttons) - drawn as 6. Check vs encoder bounce spec.
  - Jason: OK

- [x] **SW1**: Detent/pulse count unverified.
  - Jason: YOUR CHOICE IS OK

- [x] **X1**: TCXO stock thin (718); buy before ordering.
  - Jason: OK

- [x] **R27**: I2C pull-up value not fixed (PLAN 2.2-4.7k); no LCSC chosen. On +3V3D: ATtiny, Si5351, CP2102N and OLED all at 3.3 V, so I2C levels match.
  - Jason: USE 4.7K
  - KiCad EE: Applied 4.7k 0805: UNI-ROYAL 0805W8F4701T5E, C17673, basic part, 4.85 M in stock.

- [x] **R28**: as R27
  - Jason: USE 4.7K
  - KiCad EE: Applied, same as R27.

- [x] **R100**: 0603 0R series (Jason decision); LCSC code not in PLAN (C17477 is 0805).
  - Jason: USE 0805
  - KiCad EE: Applied: 0R 0805, UNI-ROYAL 0805W8F0000T5E, C17477, basic part, 5.53 M in stock.

- [x] **C100**: DC-block LF corner ~32 kHz into 50 ohm (PLAN Q6).
  - Jason: OK

- [x] **R101**: DNP shunt ~120 ohm back-match of ~85 ohm source (datasheet Zo); part/LCSC not chosen; verify return loss esp. >100 MHz.
  - Jason: OK TO DNP FOR NOW

- [x] **L1**: LQW2UAS stock 0.9-3.3k/part; buy ahead. 150n uses +/-1% C2044861 (C2043109 is +/-5%).
  - Jason: OK

- [x] **C105**: 9.1p only +/-0.25pF in stock (C513588); 24p +/-2% stock thin (C2857979, ~950).
  - Jason: OK

- [x] **J2**: Footprint is a placeholder; check BWSMA-KE-P001 launch geometry and 1.6 mm edge fit.
  - Jason: USE SMA-ENDLAUNCH FOOTPRINT FROM ETHERKITKICADLIBRARY
  - KiCad EE: Applied the EtherkitKicadLibrary:SMA-ENDLAUNCH footprint (pad 1 = center pin, pad 2 = GND on both sides plus vias, which matches Conn_Coaxial pins 1/2). The footprint isn't in this project's library table, so it only resolves where your Etherkit library is installed (ERC warns about it). LCSC C496550 BWSMA-KE-P001 (34 k in stock) is kept, but I haven't checked its body against this footprint.
  - Resolved (Jason, 2026-10-23): J2-J4 are DNP, supplied in kit, user-soldered. in_bom/in_pos_files off, LCSC cleared; MPN BWSMA-KE-P001 kept for kit sourcing. PCB: keep pads exposed and the footprint edge line on the board edge so the user can solder it by hand.

- [x] **R120**: see R100
  - Jason: USE 0805
  - KiCad EE: Applied, same as R100.

- [x] **R121**: see R100
  - Jason: USE 0805
  - KiCad EE: Already 0805, DNP. Added a 120R 0805 part for when it's fitted: UNI-ROYAL 0805W8F1200T5E, C17437, 1.34 M in stock. R101 got the same part.

- [x] **J3**: see J2
  - Jason: USE SMA-ENDLAUNCH FOOTPRINT FROM ETHERKITKICADLIBRARY
  - KiCad EE: Same as J2 (DNP, supplied in kit, user-soldered).

- [x] **R140**: see R100
  - Jason: USE 0805
  - KiCad EE: Applied, same as R100.

- [x] **R141**: see R100
  - Jason: USE 0805
  - KiCad EE: Same as R121.

- [x] **J4**: see J2
  - Jason: USE SMA-ENDLAUNCH FOOTPRINT FROM ETHERKITKICADLIBRARY
  - KiCad EE: Same as J2 (DNP, supplied in kit, user-soldered).

- [x] **JP102-JP144**: Solder-jumper footprints (SolderJumper-2_P1.3mm_*_RoundedPad1.0x1.5mm) not RF-characterised; check pad parasitics at 160 MHz on layout. Bridged (NC) trace must be cut to remove a filter; then bridge the NO bypass.
  - Jason: OK

- [x] **LPF**: LPF values (CLK0/1 60 MHz, CLK2 160 MHz): designs in /workspace/vfo/lpf60 and /workspace/vfo/lpf (ngspice + Monte Carlo); confirm on a VNA once built.
  - Jason: Will measure on actual hardware; not required before board order.

## Pre-layout items (round 3)

- [x] **DS1 supply**: DS1 pin 2 (VCC) is fed from the 3.3 V LP2985 OLED rail (through R_OLED/FB2, bulk C22-C24). HS13L01W4S01 data sheet (HS, via LCSC C5139764): Absolute Maximum Ratings give module VCC 3-5 V, logic 1.65-3.3 V; DC Characteristics give the panel's internal DC/DC input VBAT 3.5-4.2 V. Sec. 1.5/1.7 don't show what sits between pin 2 and the panel's VBAT/VDD. Pin 2 is rated to 5 V while VDD maxes at 3.3 V, so the module must carry a regulator (usually a 3.3 V LDO on these boards); at 3.3 V in, VBAT would sit below its 3.5 V minimum. 3.3 V is inside the module-pin rating but likely below the DC/DC's. No change made. Options: (a) feed DS1 VCC from +5V through R_OLED + bulk (inside the 3-5 V module rating; SPI logic stays 3.3 V from the MCU); (b) keep 3.3 V if a bench check on your sample module shows full brightness and no dropout. Suggested check: power a sample at 3.3 V and 5 V and measure its onboard regulator output.
  - Resolved (Jason): keep DS1 VCC on the 3.3 V LP2985 OLED rail (R_OLED/FB2, C22-C24 unchanged); the quiet LDO stays ahead of the module's noisy onboard regulator. DS1 is DNP (in_bom/in_pos_files off, no LCSC); supplied in kit, user-soldered (Jason sources the modules in bulk). SH1106 datasheet allows charge-pump input from 3.0 V; HS VBAT 3.5-4.2 V line looks like a template error. Bench check: on a sample module, measure the onboard LDO output at 3.3 V in and confirm full brightness. PCB: silkscreen pin names at the DS1 header.
- [x] **DS1 pinout**: switched from HS13L01W4S01 8-pin (GND,VCC,SCL,SDA,DC,CS1,FS0,CS2) to the generic retail 1.3in SH1106 SPI 7-pin, 2.54 mm: 1 GND, 2 VCC, 3 CLK/D0/SCK, 4 MOSI/D1/SDA, 5 RES, 6 DC, 7 CS (Conn_01x07, PinHeader_1x07_P2.54mm_Vertical).
  - Resolved (Jason, 2026-10-23): use the order most common on Amazon/AliExpress-type modules. DNP, supplied in kit, user-soldered. Evidence: Pololu #3760 (GND,VCC,CLK,MOS,RES,DC,CS), Estardyn/AliExpress manual (GND,VDD,SCK,SDA,RES,DC,CS), Emre's Bench SH1106 tutorial (GND,VCC,D0,D1,RES,DC,CS). Some clones swap VCC/GND: silkscreen pin names and check each kit batch before bagging.
  - Removed: R26 (CS2 pull-up), nets OLED_FS0/OLED_CS2. OLED_CS1 renamed OLED_CS.
  - **Coding PM (firmware)**: new OLED_RES on PA6 (U4 pin 4, was CS2), drive low >=10 us at boot then high before init. PA2 (pin 18, was FS0) is now free (no-connect). Pins: MOSI PA1, SCK PA3, CS PA4, DC PA5, RES PA6. SH1106 needs the 2-column offset.
  - Jason: 

- [x] **J2-J4 fit**: BWSMA-KE-P001 (BAT Wireless data sheet rev July-2-2025-A01 p.6, plus the LCSC EasyEDA model for C496550): 6.5 mm square flange; GND legs 0.9 mm thick at +/-2.55 mm centres (4.2 mm inner, 6.0 mm outer), 4.0 mm long; 1.7 mm gap between top and bottom legs (fits a 1.6 mm board); centre pin on top. SMA-ENDLAUNCH: centre pad 1.8 x 5.08 mm; GND pads 1.8 x 5.08 mm at +/-3.0 mm (2.1-3.9 mm), on top and bottom. The legs (2.1-3.0 mm) land fully on the GND pads, flush with the pads' inner edge, and the 5.08 mm pads cover the 4.0 mm legs. Footprint kept. The 1.8 mm centre pad is wider than a 50-ohm trace, which is negligible at 160 MHz.
  - Jason: 

- [x] **X1 fit**: YXC TCXO data sheet (via LCSC C48888230) p.3, 3.2x2.5 package: leads 0.6 x 0.7 mm at 2.4 x 1.7 mm pitch; recommended land 1.0 x 0.8 mm at 2.6 x 1.9 mm. Pinout (top view): 1 NC (leave floating), 2 GND, 3 Output, 4 VDD, with pin 1 bottom-left, counter-clockwise. KiCad Oscillator_SMD_SeikoEpson_SG8002CE-4Pin_3.2x2.5mm has 1.4 x 1.2 mm pads at 2.4 x 1.9 mm pitch with the same numbering, and every lead sits fully on its pad. Symbol TCXO_4P pins (1 NC/EN, 2 GND, 3 OUT, 4 VDD) match. Footprint kept.
  - Jason: 

- [x] **Library**: EtherkitKicadLibrary now resolves from the project-local PCB/lib folder via PCB/sym-lib-table and PCB/fp-lib-table (${KIPRJMOD}). Etherkit.pretty holds SMA-ENDLAUNCH and EtherkitLogoSmall, copied unchanged from github.com/etherkit/EtherkitKicadLibrary @6b9fc0f. Etherkit.kicad_sym holds LOGO, copied from the copy embedded in your review commit 4963a6d (the public library has no LOGO symbol). ERC: 0 errors, 0 warnings.
  - Jason: 

- [x] **Title block**: comment 1 on all sheets changed to "Draft schematic, not reviewed. Open items: docs/VERIFY.md".
  - Jason: 

## Layout round 1 changes
- [x] **SW2-SW4**: taller front-panel tact switch, no caps.
  - Resolved (Jason, 2026-10-23): TS-1187A (5.1x5.1, ~1.5 mm) replaced by Kinghelm KH-6X6X11H-STM, 6x6 mm SMD, 11 mm actuator height, LCSC C2837537 (14,430 in stock 2026-10-23, ~$0.04). JLC-assembled, not DNP: SMD stock is solid, so no THT kit part is needed. Height: OLED glass top ~5.2 mm above PCB (2.5 mm header); EC11 body 6.5 mm, so a 1.6 mm panel resting at ~8 mm puts the panel face at ~9.6 mm, leaving ~3-4 mm of M7 bushing thread for the nut. An 11 mm actuator then sits ~1.4 mm proud of the panel face, flush-ish with a finger, far below the 20 mm encoder shaft. Panel holes ~4 mm for the 3.5 mm round actuator. Alternative heights in the same family if the panel spacing changes: KH-6X6X10H-STM C2837536, KH-6X6X13H-STM C2837539. Bench check: confirm the actuator protrusion against the real panel and standoff height.
- [x] **H1-H4**: plated M3 mounting holes tied to GND.
  - Resolved (Jason, 2026-10-23): symbol Mechanical:MountingHole_Pad (1 pin) with a GND power symbol on each; footprint MountingHole:MountingHole_3.2mm_M3_Pad_Via (3.2 mm plated hole, 6.4 mm annular pad both sides, 8 stitching vias into the planes). Not in BOM/position files. PCB: no visible silkscreen at the holes. Check: chassis/standoffs then bond the board ground to the enclosure.
- [x] **SH1**: optional RF shield, DNP.
  - Resolved (Jason, 2026-10-23): no off-the-shelf can fits the RF block with stock. Closest on LCSC: MYOUNG MY-PBZ-02 (C7525435, 42.28 mm square, 1,465 stock) is too tall for the space between the SMAs and the panel controls; MY-PBZ-06 (45.3x29.15 mm) has 22 in stock; MY-PBZ-05 (50.65x32.3 mm) has none. So SH1 is a custom solder fence, EtherkitKicadLibrary:RF_Fence_42x33.5mm: 1.0 mm exposed GND strip, 42 x 33.5 mm outside, GND vias 0.3/0.6 mm at <=2.5 mm pitch (lambda/20 at 1 GHz is 15 mm, so plenty of margin), 2.4 mm notches in the top wall for the three SMA feed lines. Symbol Mechanical:MountingHole_Pad on GND, DNP, not in BOM/position files. The user solders on a cut tin can. PCB: other signals leave the fenced area on inner layers only. Check: the fit with a 0.2 mm tin-plate can.
