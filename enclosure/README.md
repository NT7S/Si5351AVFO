# Si5351A VFO 3D-printed enclosure (first iteration)

> **Status:** first iteration, pending a physical fit check on a printed case. Dimensions may change after that test.

Two-part supportless case for the Si5351A VFO board (100 × 65 mm). The case is 105 × 70 × 17.5 mm overall.

- **Front shell:** the panel, walls and screw bosses. It has a window and stops for the 1.3" OLED, holes for the BAND UP / BAND DOWN / MENU buttons and the TUNE (push: STEP) encoder, and openings for USB-C and the CLK0/1/2 SMA jacks. The product name, Etherkit logo and labels are debossed 0.5 mm.
- **Back cover:** a plate with standoffs that clamps the PCB with 4 screws through its M3 holes.

## Contents

| Folder | What's in it |
|---|---|
| `src/` | CadQuery source: `vfo_case.py` (case), `labels.py` (panel text and logo), `etherkit_logo_ekm.json` (logo outline from the EtherKeyerMini case), `fitcheck.py`, `render.py` |
| `stl/` | `vfo_front_shell.stl`, `vfo_back_cover.stl` (in print orientation) |
| `step/` | `vfo_front_shell.step`, `vfo_back_cover.step` |
| `3mf/` | `vfo_case_plate.3mf`: both parts on one Elegoo Centauri Carbon 2 plate, PETG |
| `renders/` | Preview renders |

## Print settings

Tested with an Elegoo Centauri Carbon 2.

| Setting | Value |
|---|---|
| Nozzle | 0.4 mm |
| Filament | Elegoo PETG PRO, 240 °C nozzle / 70 °C bed |
| Layer height | 0.16 mm first layer, then 0.20 mm |
| Walls | 3 |
| Top / bottom layers | 4 / 5 |
| Infill | 15 % gyroid |
| Supports / brim | None |
| Elephant-foot compensation | 0.1 mm |
| Orientation | Front shell face-down; back cover outer side down |
| Estimate | About 2 h 27 min and 46 g for both parts |

## Build steps

1. **Encoder hole:** a 0.2 mm skin prints over the encoder shaft hole so that the recess above it bridges cleanly. After printing, cut it out to 7.6 mm diameter (hobby knife or a 7.5–8 mm drill by hand).
2. **OLED header:** after soldering the OLED module's 7-pin header, trim the pins flush. The panel is solid over the header.
3. Fit the board into the front shell, fit the back cover, and fasten it with the 4 screws.
4. Fit the encoder washer and nut on the front, then add the knob. The shaft tip sits 24.5 mm above the PCB.

## Hardware

| Qty | Part |
|---|---|
| 4 | M3 × 12 countersunk screws (ISO 10642 / DIN 7991) |
| 4 | M3 heat-set inserts for a 4.0 mm hole × 6 mm deep (or set `FASTENER = "selftap"` in `vfo_case.py` for 2.6 mm self-tapping holes) |
| 1 | M7 × 0.75 hex nut, 11 mm AF × 2 mm, for the Alps EC11E18244A5 encoder (**not supplied with the encoder**) |
| 1 | Washer, 12 mm OD / 7.1 mm ID × 0.5 mm |

The panel text uses **Fira Code Bold** (SIL Open Font License, https://github.com/tonsky/FiraCode). The font file is not included in this repo.

## Regenerating

Requires CadQuery 2.8 and shapely (plus pyvista and trimesh for `render.py` and `fitcheck.py`):

```sh
python3 -m venv ~/.venvs/cad
~/.venvs/cad/bin/pip install cadquery==2.8.0 shapely trimesh pyvista
# put FiraCode-Bold.ttf at ~/cad/fonts/ (or edit FONT in labels.py)
cd enclosure/src
~/.venvs/cad/bin/python vfo_case.py      # writes the STEP/STL exports
```

`fitcheck.py` and `render.py` load the board model from `docs/mechanical/Si5351AVFO_board.step`, using paths relative to the working directory. Adjust the path if you run them from `enclosure/src`.
