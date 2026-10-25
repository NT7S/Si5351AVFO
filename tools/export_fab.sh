#!/usr/bin/env bash
# JLCPCB fab + PCBA outputs into PCB/production/. Fails on ERC/DRC errors other than the
# 15 accepted SMA edge-launch copper_edge_clearance hits (J2/J3/J4).
set -euo pipefail
cd "$(dirname "$0")/.."
B=PCB/Si5351AVFO; O=PCB/production; G=$O/gerbers
rm -rf "$O"; mkdir -p "$G"
kicad-cli sch erc -o $O/erc.rpt --format report --units mm --severity-warning --severity-error --exit-code-violations $B.kicad_sch
kicad-cli pcb drc -o $O/drc.rpt --format report --units mm --severity-warning --severity-error --refill-zones --schematic-parity $B.kicad_pcb
n=$(grep -c '^\[' $O/drc.rpt || true); e=$(grep -c '^\[copper_edge_clearance' $O/drc.rpt || true)
[ "$n" = 15 ] && [ "$e" = 15 ] || { echo "DRC: unexpected violations ($n total)"; exit 1; }
kicad-cli pcb export gerbers -o $G --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --precision 6 --no-protel-ext $B.kicad_pcb
kicad-cli pcb export drill -o $G/ --format excellon --drill-origin absolute --excellon-units mm \
  --excellon-zeros-format decimal --excellon-separate-th $B.kicad_pcb
kicad-cli sch export bom -o $O/raw_bom.csv \
  --fields 'Value,Reference,Footprint,LCSC,${DNP},${EXCLUDE_FROM_BOM}' --labels 'Comment,Designator,Footprint,LCSC,DNP,EXB' \
  --group-by 'Value,Footprint,LCSC,${DNP}' --sort-field Reference --exclude-dnp $B.kicad_sch
python3 - "$O" <<'P'
import csv,sys
o=sys.argv[1]; r=list(csv.DictReader(open(o+'/raw_bom.csv')))
w=csv.writer(open(o+'/Si5351AVFO_BOM_JLC.csv','w',newline=''))
w.writerow(['Comment','Designator','Footprint','LCSC Part #'])
for x in r:
    if x['DNP'] or x['EXB']: continue
    w.writerow([x['Comment'],x['Designator'],x['Footprint'].split(':')[-1],x['LCSC']])
P
rm $O/raw_bom.csv
kicad-cli pcb export pos -o $O/raw_pos.csv --format csv --units mm --side both --exclude-dnp $B.kicad_pcb
python3 - "$O" <<'P'
import csv,sys
o=sys.argv[1]; w=csv.writer(open(o+'/Si5351AVFO_CPL_JLC.csv','w',newline=''))
w.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
for x in csv.DictReader(open(o+'/raw_pos.csv')):
    if x['Ref'].startswith('FID'): continue
    w.writerow([x['Ref'],x['PosX']+'mm',x['PosY']+'mm','Top' if x['Side']=='top' else 'Bottom',x['Rot']])
P
rm $O/raw_pos.csv
python3 -c "import zipfile,os,sys;g=sys.argv[1];z=zipfile.ZipFile(sys.argv[2],'w',zipfile.ZIP_DEFLATED);[z.write(os.path.join(g,f),f) for f in sorted(os.listdir(g))]" $G $O/Si5351AVFO_gerbers_JLC.zip
echo done
