# pcbgen: scripted layout for PCB/Si5351AVFO.kicad_pcb

Regenerates the board from scratch (KiCad 10 Python via flatpak `org.kicad.KiCad`):

1. `gen_pcb.py` – outline, placement, rule areas/keepouts, 3D models
2. `stackup.py` – JLC 4-layer stackup
3. `route_rf.py` – CLK0-2 0.31/0.20 mm CPWG chains (U2 rotated: CLK0/1/2 leave the top row on F.Cu straight into 0402 series Rs), LPF, select/bypass jumpers
4. `gnd.py` – GND vias at every SMD GND pad, fence/SMA stitching
5. `post_route.py` – imports the freerouting session `fr.ses` (`ROUTE=power` keeps power nets only)
6. `pours.py` – F/B GND pours, fill
7. DRC + renders

`fr.sh` exports the DSN (planes/OLED footprint keepout removed, `dsnfilt.py` drops pre-routed RF nets,
marks In1 as a plane layer, clearance 0.17) and runs Freerouting 2.5.0 (`freerouting.jar`, Java 25).
`fd2d.py` is the 2D finite-difference CPWG impedance solver used to sanity-check the 50 ohm geometry.

Scripts currently use absolute paths `/workspace/build` (scripts, fr.ses, freerouting.jar) and
`/workspace/Si5351AVFO` (repo); copy this folder to `/workspace/build` or adjust the paths.
Run: `bash run.sh` (rebuild + import fr.ses), `bash fr.sh` (re-autoroute, then `bash run.sh` again).

## Fab notes
- **Controlled impedance 50 ohm, L1/L2, 0.31/0.20, per JLC calculator.** JLC04161H-7628 stackup, coplanar
  single-ended, L1 referenced to L2 (In1 GND), 1 oz outer: 0.3058 mm for 50 ohm at a 0.20 mm gap -> RF50
  netclass, all RF tracks and SMA launches use 0.31 mm / 0.20 mm. GND fence vias sit 1.0 mm off each RF centreline.
- **U3 (CP2102N) exposed-pad vias are tented both sides and filled** (via properties set in `gnd.py`);
  order with via covering/epoxy fill so solder does not wick off the thermal pad.
- `+3V3_CLK` is routed only on In2/B.Cu (DSN class `PWRCLK`); inside the RF fence only pad-to-via stubs are on F.Cu.
  In2 is kept solid (keepout) under all RF/clock lines.
- `+5V` (USB VBUS) tracks are widened to 0.45 mm by `post_route.py` wherever they clear 0.17 mm.
- Fiducials FID1-FID3 (1 mm / 2 mm mask) for JLC PCBA. Fab notes are drawn on User.1 below the outline.
- `PCB/Si5351AVFO.kicad_dru`: courtyard exemptions for U2's tight decoupling/series Rs and J1 footprint-internal rules.
- SW2-SW4 are soft buttons (labels drawn on the OLED); no board legend for them.

## Helpers (review-fix pass, Oct 2026)
- `models.py` – simple CadQuery 3D models in `PCB/lib/Etherkit.3dshapes` (run with a CadQuery venv, e.g. `/workspace/.venv-cq/bin/python`)
- `mkfp.py` – project footprints
- `astar.py NET x0 y0 x1 y1 width LAYER[,LAYER2]` – small grid router used for single-net fixes (coords relative to origin 100,100)
- `stitch.py sma2|fence X,X,...` – adds GND stitching vias with clearance checks (SMA launch flanks, filter fence lines)

Note: the board on `pcb-layout` also carries hand fixes made after the last full regeneration (+3V3_CLK FB1->U2 route,
CP_VBUS_SENSE B.Cu hop, SMA/fence stitching vias, C4/C27/C28 moves). `gen_pcb.py` has the updated placements, but a full
`run.sh` rebuild plus the current `fr.ses` will not reproduce those routes exactly. Treat `PCB/Si5351AVFO.kicad_pcb` as the source of truth.
