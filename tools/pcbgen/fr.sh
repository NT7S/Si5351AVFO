set -e
cd /workspace/build
flatpak run --filesystem=/workspace --command=python3 org.kicad.KiCad -c "import pcbnew;b=pcbnew.LoadBoard('/workspace/Si5351AVFO/PCB/Si5351AVFO.kicad_pcb');[b.Remove(z) for z in list(b.Zones()) if z.GetZoneName() in ('OLED_KEEPOUT','GND_F.Cu','GND_B.Cu','GND_In2.Cu')];print(pcbnew.ExportSpecctraDSN(b,'/workspace/build/fr.dsn'))"
python3 dsnfilt.py && /usr/lib/jvm/java-25-openjdk-amd64/bin/java -jar freerouting.jar -de fr.dsn -do fr.ses -mp 600 --gui.enabled=false
