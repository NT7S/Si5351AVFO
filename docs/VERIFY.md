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

- [x] **R120**: see R100
  - Jason: USE 0805
  - KiCad EE: Applied, same as R100.

- [x] **R121**: see R100
  - Jason: USE 0805
  - KiCad EE: Already 0805, DNP. Added a 120R 0805 part for when it's fitted: UNI-ROYAL 0805W8F1200T5E, C17437, 1.34 M in stock. R101 got the same part.

- [x] **J3**: see J2
  - Jason: USE SMA-ENDLAUNCH FOOTPRINT FROM ETHERKITKICADLIBRARY
  - KiCad EE: Same as J2.

- [x] **R140**: see R100
  - Jason: USE 0805
  - KiCad EE: Applied, same as R100.

- [x] **R141**: see R100
  - Jason: USE 0805
  - KiCad EE: Same as R121.

- [x] **J4**: see J2
  - Jason: USE SMA-ENDLAUNCH FOOTPRINT FROM ETHERKITKICADLIBRARY
  - KiCad EE: Same as J2.

- [x] **JP102-JP144**: Solder-jumper footprints (SolderJumper-2_P1.3mm_*_RoundedPad1.0x1.5mm) not RF-characterised; check pad parasitics at 160 MHz on layout. Bridged (NC) trace must be cut to remove a filter; then bridge the NO bypass.
  - Jason: OK

- [ ] **LPF**: LPF values (CLK0/1 60 MHz, CLK2 160 MHz): designs in /workspace/vfo/lpf60 and /workspace/vfo/lpf (ngspice + Monte Carlo); confirm on a VNA once built.
  - Jason: 
