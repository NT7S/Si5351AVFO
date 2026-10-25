# Si5351A VFO 3D-printed enclosure (rev4)

> **Status:** rev4, printed in two-color PETG on an Elegoo Centauri Carbon 2 and checked with the knob fitted. Dimensions may still change once the board's final STEP is available.

Two-part supportless case for the Si5351A VFO board (100 × 65 mm). The case is 105 × 70 × 17.5 mm overall.

- **Front shell:** the panel, walls and screw bosses. It has a window and stops for the 1.3" OLED, holes for the three push buttons and the encoder, and openings for USB-C and the CLK0/1/2 SMA jacks. The product name, Etherkit logo and labels are a flush second-color inlay (white in black), 0.6 mm deep.
  - The three buttons are display soft keys, so they have no panel labels.
  - The encoder label is two lines, "TUNE/" over "STEP", centered on the shaft and placed so a 20 mm knob does not cover it.
  - Text uses Barlow Bold, and Barlow Semi Condensed Bold for the tight CLK0/1/2 row. Strokes narrower than 0.8 mm are widened (`INLAY_MIN_STROKE` in `vfo_case.py`) so small text prints solid with a 0.4 mm nozzle.
- **Back cover:** a plate with standoffs that clamps the PCB with 4 screws through its M3 holes.

## Contents

| Folder | What's in it |
|---|---|
| `src/` | CadQuery source: `vfo_case.py` (case), `labels.py` (panel text and logo), `etherkit_logo_ekm.json` (logo outline from the EtherKeyerMini case), `fitcheck.py`, `render.py` |
| `fonts/` | Barlow Bold and Barlow Semi Condensed Bold, with `OFL.txt` (SIL Open Font License 1.1) |
| `stl/` | Print orientation: `vfo_front_shell_body.stl` + `vfo_front_shell_inlay.stl` (two-color front), `vfo_front_shell.stl` (single-color front), `vfo_back_cover.stl` |
| `step/` | Print orientation: `vfo_front_shell.step`, `vfo_front_shell_2color.step` (body + inlay assembly), `vfo_back_cover.step`. Board frame: `*_assembly_frame.step` |
| `3mf/` | `VFO_case_2color_PETG_CC2_rev4.3mf`: OrcaSlicer project, both parts on one Centauri Carbon 2 plate |
| `gcode/` | `VFO_case_2color_PETG_CC2_rev4.gcode`: the sliced job that was printed |
| `renders/` | Preview renders from the first iteration (they show the older debossed labels) |

## Print settings

Printed on an Elegoo Centauri Carbon 2, Textured PEI plate.

| Setting | Value |
|---|---|
| Nozzle | 0.4 mm |
| Filament | T0 Elegoo PETG PRO black (case), T1 generic PETG white (inlay). 240 °C nozzle; bed 75 °C first layer, then 70 °C |
| Layer height | 0.20 mm |
| Walls | 3 |
| Top / bottom layers | 4 / 5 |
| Infill | 15 % gyroid |
| Supports / brim | None. Prime tower 20 mm |
| Elephant-foot compensation | 0.1 mm |
| Orientation | Front shell face-down; back cover outer side down |
| Estimate | 1 h 43 min, about 29 g (28.6 g black, 0.4 g white) for both parts |

## Build steps

1. **Encoder hole:** a 0.2 mm skin prints over the encoder shaft hole so that the recess above it bridges cleanly. After printing, cut it out to 7.6 mm diameter (hobby knife or a 7.5–8 mm drill by hand).
2. **OLED header:** after soldering the OLED module's 7-pin header, trim the pins flush. The panel is solid over the header.
3. Fit the board into the front shell, fit the back cover, and fasten it with the 4 screws.
4. Fit the encoder washer and nut on the front, then add the knob (20 mm diameter or smaller). The shaft tip sits 24.5 mm above the PCB.

## Hardware

| Qty | Part |
|---|---|
| 4 | M3 × 12 countersunk screws (ISO 10642 / DIN 7991) |
| 4 | M3 heat-set inserts for a 4.0 mm hole × 6 mm deep (or set `FASTENER = "selftap"` in `vfo_case.py` for 2.6 mm self-tapping holes) |
| 1 | M7 × 0.75 hex nut, 11 mm AF × 2 mm, for the Alps EC11E18244A5 encoder (**not supplied with the encoder**) |
| 1 | Washer, 12 mm OD / 7.1 mm ID × 0.5 mm |

## Regenerating

Requires CadQuery 2.8 and shapely (plus pyvista and trimesh for `render.py` and `fitcheck.py`). All paths are relative to the script files, so the scripts run from any working directory. The fonts are loaded from `enclosure/fonts/`, and the board model from `docs/mechanical/Si5351AVFO_board.step`.

```sh
python3 -m venv ~/.venvs/cad
~/.venvs/cad/bin/pip install cadquery==2.8.0 shapely trimesh pyvista
~/.venvs/cad/bin/python enclosure/src/vfo_case.py   # writes STEP/STL exports into enclosure/src/
mv enclosure/src/*.step enclosure/step/ && mv enclosure/src/*.stl enclosure/stl/
```

Set `PANEL_GRAPHICS = True` in `vfo_case.py` for single-color debossed graphics instead of the inlay.
