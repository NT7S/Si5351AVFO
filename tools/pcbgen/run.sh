set -e
K(){ cp PCB/Si5351AVFO.kicad_pcb /tmp/k_snap.pcb; sleep 1; for i in 1 2 3; do cp -p /tmp/k_snap.pcb PCB/Si5351AVFO.kicad_pcb; flatpak run --filesystem=/workspace --env=ROUTE=${ROUTE:-all} --command=python3 org.kicad.KiCad "$@" && return 0; [ PCB/Si5351AVFO.kicad_pcb -nt /tmp/k_snap.pcb ] && return 0; echo RETRY $1; done; return 1; }
cd /workspace/Si5351AVFO
flatpak run --filesystem=/workspace --command=python3 org.kicad.KiCad /workspace/build/gen_pcb.py 2>&1 | grep -v Gtk
python3 /workspace/build/stackup.py
K /workspace/build/route_rf.py
K /workspace/build/gnd.py
[ -f /workspace/build/fr.ses ] && K /workspace/build/post_route.py || true
K /workspace/build/pours.py
kicad-cli pcb drc --schematic-parity --severity-all -o /workspace/build/drc.rpt PCB/Si5351AVFO.kicad_pcb >/dev/null
grep -E "^\[" /workspace/build/drc.rpt | sed 's/\]:.*/]/' | sort | uniq -c
R="kicad-cli pcb render --use-board-stackup-colors --width 2000 --height 1400 PCB/Si5351AVFO.kicad_pcb"
$R --side top --quality basic --zoom 1 -o /workspace/Si5351AVFO_top.png >/dev/null
$R --side top --rotate "-40,0,25" --perspective --quality high --zoom 0.9 -o /workspace/Si5351AVFO_3d.png >/dev/null
