# Si5351AVFO
Si5351A VFO board for the Si5351 Field Manual (Chapter 6).

## Regenerating docs

After any schematic change, run `tools/export_docs.sh` (needs KiCad 10 `kicad-cli`).
It rewrites `docs/Si5351AVFO_schematic.pdf`, the netlist, SVGs and `docs/erc.rpt`.
