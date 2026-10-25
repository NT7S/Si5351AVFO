# Si5351A VFO firmware

Firmware for the NT7S Si5351A VFO board (Si5351 Field Manual ch. 6): ATtiny3226,
Si5351A with 25 MHz TCXO, 1.3" SH1106 OLED, encoder, three soft buttons and
USB-C serial. Requirements: `REQUIREMENTS.md` rev 3.1 (kept with the project docs).

Status: **skeleton, v0.1.0.** Compiles; not yet run on hardware.

## Build

Board settings (either build method):

| Setting | Value |
|---|---|
| Core | megaTinyCore 2.6.11 |
| Board | ATtiny3226 w/Optiboot |
| Clock | 8 MHz internal |
| Reset pin | UPDI on PA0, RST on PB4 |
| BOD | disabled (enabling it is an optional fuse change, see REQUIREMENTS §3) |
| Startup time | 8 ms |
| EEPROM | retained (EESAVE) |

The bootloader and fuses are burned once over UPDI (J5). After that, sketches
upload over USB-C through Optiboot at 115200 baud (DTR auto-reset on PB4).

### Arduino IDE
1. Install megaTinyCore 2.6.11 (Boards Manager URL
   `http://drazzy.com/package_drazzy.com_index.json`).
2. Install Si5351Arduino v2.4.1 or later (until it is released, use the
   `v2.4.1-fixes` branch, commit 1c7199f).
3. Open `Si5351AVFO/Si5351AVFO.ino`, set the options above, Burn Bootloader
   once over UPDI, then Upload.

### PlatformIO
```
cd firmware
pio run                 # build
pio run -t upload       # upload via Optiboot on the USB serial port
```
`platformio.ini` pins Si5351Arduino to commit 1c7199f. Add
`build_flags = -DENABLE_SERIAL=0` to drop the serial interface (flash emergencies only).

## Size (skeleton, avr-gcc 7.3.0, -Os, LTO)

| Build | Flash | RAM |
|---|---:|---:|
| Full (serial on, rev 3.5) | 28,243 B of 32,256 B (87.6%) | 662 B of 3,072 B (21.5%) |
| `ENABLE_SERIAL=0` (measured at an earlier revision) | 21,360 B (66.2%) | 474 B |

Si5351Arduino is about 8.9 KB of this. See the flash-optimization notes in the
requirements (§10) if space gets tight.

## Structure

Files marked **host** use only `<stdint.h>` and can be compiled and unit-tested
on a PC with `g++ -std=c++11`.

| File | Purpose |
|---|---|
| `Si5351AVFO.ino` | `setup()` / `loop()`: poll input, dispatch, serial, delayed save, redraw |
| `config.h` | version, reference frequency, timings, label positions, encoder options |
| `pins.h` | ATtiny3226 pin map (requirements §2) |
| `vfo_state.h` | **host** – the `VfoState` struct (everything that is saved) |
| `bands.h/.cpp` | **host** – band table 160 m–2 m, band step with wrap, tuning-limit clamp, defaults |
| `tuning.h/.cpp` | **host** – step table and cycling, `MMM.KKK.HHH` formatting, step underline position (500 Hz on the '.'), encoder decoder |
| `modes.h/.cpp` | **host** – Direct / Superhet / Quadrature output plan, I/Q integer PLL plan (4.76–90 MHz), LPF mute unless overridden |
| `eeprom_layout.h/.cpp` | **host** – 128-byte EEPROM slot image (A/B slots), CRC8, validation |
| `cmd_parser.h/.cpp` | **host** – serial line tokenizer, command table, number parsing |
| `vfo.h/.cpp` | owns the state, programs the Si5351 (PLL routing, I/Q phase, drive, enables) |
| `settings.h/.cpp` | EEPROM load, 5 s delayed save, immediate save |
| `input.h/.cpp` | encoder (pin-change interrupt) and debounced buttons → events |
| `ui.h/.cpp` | main screen, menu list, value editor, soft-key labels |
| `serialcmd.h/.cpp` | executes serial commands, `STATUS` line |
| `sh1106.h/.cpp` | minimal SH1106 SPI driver, no frame buffer |

## Controls

| Screen | Encoder | Push | SW2 | SW3 | SW4 |
|---|---|---|---|---|---|
| Main | tune by step | cycle step 100k→10k→1k→500→100→10 Hz | BAND- | BAND+ | MENU |
| Menu list | scroll | enter item | page up | page down | back |
| Value edit | change value | save | cursor left | cursor right | cancel |

## Serial (115200 8N1, line-based, case-insensitive)
`F <Hz>`, `F?`, `STEP <Hz>`, `STEP?`, `BAND <name|+|->`, `BAND?`, `MODE <DIR|SH|IQ>`,
`MODE?`, `ON <clk>`, `OFF <clk>`, `DRIVE <clk> <2|4|6|8>`, `IF <Hz>`, `IF?`,
`INJ <HI|LO>`, `IQ <0|1>`, `LIMIT <HAM|WIDE>`, `FOVR <clk> <0|1>`, `MS <n>`,
`MR <n>`, `MC <n>`, `M?`, `CAL <ppb>`, `CAL?`, `SAVE`, `RESET`, `RESET ALL`, `DEFAULTS`, `STATUS`, `VER`,
`HELP`. `AUTO` is not implemented yet. Replies are `OK`, `ERR <reason>` or data.
`MODE IQ` and `MR` of a quadrature memory reply `ERR IQRANGE` when the frequency is
outside the quadrature range (4.761905–90 MHz); nothing is changed.

## EEPROM layout upgrade
Settings use two 128-byte slots (A/B, layout version 2); each save goes to the older
slot, so each byte is written every other save. A board flashed with the old
single-slot layout (version 1) finds no valid slot after the upgrade and boots once
with defaults, losing its calibration and memories. Note the calibration value
(`CAL?`) before upgrading if you need it.

## To verify on hardware
- Encoder detent count (`ENC_QUARTERS_PER_DETENT`) and direction (`ENC_REVERSE`).
- SH1106 column offset (2) and soft-key label positions (x = 18/64/110 px).
- I/Q phase relationship on a scope; CLK0/1 levels through the LPFs.

## License
MIT (see `LICENSE`). Si5351Arduino is GPL-3.0 for now, so a distributed binary
that includes it falls under GPL-3.0 terms until the library is relicensed.
