J1: UART adapter schematic pairs GCT USB4105 footprint with this HCTL LCSC part; HCTL footprint used here - confirm. Shield to GND assumed (not stated in PLAN). - OK
D1: Pin-to-line mapping (D-/D+/VBUS on pins 2/3/4) to be checked against adapter layout. - OK
C10: LCSC stock low; fallback C49678 (0805) per PLAN - ACKNOWLEDGED
U3: Unused CP2102N pins left NC (adapter used DTR via JP1, TRRS dropped). Confirm none were strapped on the adapter. - OK
R9: PLAN says /RST pull-up to VBUS (as on adapter); CP2102N RST max is VIO-referenced - confirm adapter really ties to VBUS. - INVESTIGATE FURTHER
FB2: Bead or series R (<=6 ohm upper bound, PLAN 4a); value to be set by measurement. - OK
C22: OLED bulk value: PLAN start point 2x4.7u, tune by measurement - INVESTIGATE FURTHER
C24: DNP 1206 site for larger OLED bulk cap; value/part not chosen - INVESTIGATE FURTHER
U4: Pin mux (PLAN sec.3) to be checked vs datasheet I/O mux table. Jason consigning parts. - EVERYTHING OK BUT DOUBLE-CHECK UART PINS
C14: PLAN: series R or clamp on PB4 for DTR-rising overshoot? EKM has none. - INVESTIGATE FURTHER
J5: Replicated from EtherKeyerMini (J3); EKM has no LCSC/MPN fields - part number to choose. - 0.1" HEADER
R13: Replicated from EtherKeyerMini (R3); EKM has no LCSC/MPN fields - part number to choose. - YOU CHOOSE
D4: Replicated from EtherKeyerMini (D1); EKM has no LCSC/MPN fields - part number to choose. - YOU CHOOSE A SUITABLE SMT REPLACEMENT
DS1: 1.3in SPI SH1106 module. Pin order GND,VCC,SCL,SDA,DC,CS1,FS0,CS2 from PLAN pin list; pin numbering, pitch and connector style unverified. Low stock - Jason sourcing. - OK
C17: Debounce topology/count: PLAN lists x5 but 6 inputs (A,B,SW,3 buttons) - drawn as 6. Check vs encoder bounce spec. - OK
SW1: Detent/pulse count unverified. - YOUR CHOICE IS OK
X1: TCXO stock thin (718); buy before ordering. - OK
R27: I2C pull-up value not fixed (PLAN 2.2-4.7k); no LCSC chosen. On +3V3D: ATtiny, Si5351, CP2102N and OLED all at 3.3 V, so I2C levels match. - USE 4.7K
R28: as R27 - USE 4.7K
R100: 0603 0R series (Jason decision); LCSC code not in PLAN (C17477 is 0805). - USE 0805
C100: DC-block LF corner ~32 kHz into 50 ohm (PLAN Q6). - OK
R101: DNP shunt ~120 ohm back-match of ~85 ohm source (datasheet Zo); part/LCSC not chosen; verify return loss esp. >100 MHz. - OK TO DNP FOR NOW
L1: LQW2UAS stock 0.9-3.3k/part; buy ahead. 150n uses +/-1% C2044861 (C2043109 is +/-5%). - OK
C105: 9.1p only +/-0.25pF in stock (C513588); 24p +/-2% stock thin (C2857979, ~950). - OK
J2: Footprint is a placeholder; check BWSMA-KE-P001 launch geometry and 1.6 mm edge fit. - USE SMA-ENDLAUNCH FOOTPRINT FROM ETHERKITKICADLIBRARY
R120: see R100 - USE 0805
R121: see R100 - USE 0805
J3: see J2 - USE SMA-ENDLAUNCH FOOTPRINT FROM ETHERKITKICADLIBRARY
R140: see R100 - USE 0805
R141: see R100 - USE 0805
J4: see J2 - USE SMA-ENDLAUNCH FOOTPRINT FROM ETHERKITKICADLIBRARY
JP102-JP144: Solder-jumper footprints (SolderJumper-2_P1.3mm_*_RoundedPad1.0x1.5mm) not RF-characterised; check pad parasitics at 160 MHz on layout. Bridged (NC) trace must be cut to remove a filter; then bridge the NO bypass. - OK
LPF values (CLK0/1 60 MHz, CLK2 160 MHz): designs in /workspace/vfo/lpf60 and /workspace/vfo/lpf (ngspice + Monte Carlo); confirm on a VNA once built.
