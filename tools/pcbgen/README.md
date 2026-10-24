# pcbgen: scripted layout for PCB/Si5351AVFO.kicad_pcb

Regenerates the board from scratch (KiCad 10 Python via flatpak `org.kicad.KiCad`):

1. `gen_pcb.py` – outline, placement, rule areas/keepouts, 3D models
2. `stackup.py` – JLC 4-layer stackup
3. `route_rf.py` – CLK0-2 0.35/0.20 mm CPWG chains, LPF, select/bypass jumpers
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
