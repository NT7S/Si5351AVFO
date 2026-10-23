J1: UART adapter schematic pairs GCT USB4105 footprint with this HCTL LCSC part; HCTL footprint used here - confirm. Shield to GND assumed (not stated in PLAN).
D1: Pin-to-line mapping (D-/D+/VBUS on pins 2/3/4) to be checked against adapter layout.
C10: LCSC stock low; fallback C49678 (0805) per PLAN
U3: Unused CP2102N pins left NC (adapter used DTR via JP1, TRRS dropped). Confirm none were strapped on the adapter.
R9: PLAN says /RST pull-up to VBUS (as on adapter); CP2102N RST max is VIO-referenced - confirm adapter really ties to VBUS.
FB2: Bead or series R (<=6 ohm upper bound, PLAN 4a); value to be set by measurement.
C22: OLED bulk value: PLAN start point 2x4.7u, tune by measurement
C24: DNP 1206 site for larger OLED bulk cap; value/part not chosen
U4: Pin mux (PLAN sec.3) to be checked vs datasheet I/O mux table. Jason consigning parts.
D6: ATtiny-only rail +3V3_MCU: diode-OR of +3V3D (D6) and UPDI header VCC (D5) so a programmer cannot back-feed +3V3D. Same 1N5711 as EKM D5 (no LCSC/MPN). MCU VDD ~2.9-3.0 V (0.3-0.4 V drop): check ATtiny VIH/VIL vs CP2102N TXD (3.3 V VIO, exceeds MCU VDD by ~0.35 V) and OLED/Si5351 3.3 V logic; I/O pull-ups moved to +3V3_MCU. With only programmer power, MCU pins can back-power unpowered CP2102N/OLED/Si5351 via their ESD diodes.
C14: PLAN: series R or clamp on PB4 for DTR-rising overshoot? EKM has none.
J5: Replicated from EtherKeyerMini (J3); EKM has no LCSC/MPN fields - part number to choose.
D5: Replicated from EtherKeyerMini (D2); EKM has no LCSC/MPN fields - part number to choose.
R13: Replicated from EtherKeyerMini (R3); EKM has no LCSC/MPN fields - part number to choose.
D4: Replicated from EtherKeyerMini (D1); EKM has no LCSC/MPN fields - part number to choose.
DS1: 1.3in SPI SH1106 module. Pin order GND,VCC,SCL,SDA,DC,CS1,FS0,CS2 from PLAN pin list; pin numbering, pitch and connector style unverified. Low stock - Jason sourcing.
C17: Debounce topology/count: PLAN lists x5 but 6 inputs (A,B,SW,3 buttons) - drawn as 6. Check vs encoder bounce spec.
SW1: Detent/pulse count unverified.
X1: TCXO stock thin (718); buy before ordering.
R27: I2C pull-up value not fixed (PLAN 2.2-4.7k); no LCSC chosen. Pulled to +3V3_MCU (not +3V3_CLK) so SCL/SDA never exceed ATtiny VDD; Si5351 VIH 0.7*VDD=2.31 V vs ~2.95 V high - check.
R28: as R27
R100: 0603 0R series (Jason decision); LCSC code not in PLAN (C17477 is 0805).
C100: DC-block LF corner ~32 kHz into 50 ohm (PLAN Q6).
R101: DNP shunt ~120 ohm back-match of ~85 ohm source (datasheet Zo); part/LCSC not chosen; verify return loss esp. >100 MHz.
L1: LPF inductor size (SMD vs T37 option, PLAN Q7)
C105: Parallel C across L (elliptic) per LowPassFilterModule - unconfirmed
C101: LPF values builder choice (DNP)
J2: Footprint is a placeholder; check BWSMA-KE-P001 launch geometry and 1.6 mm edge fit.
R120: see R100
R121: see R100
J3: see J2
R140: see R100
R141: see R100
J4: see J2
