# Scripts

Python 3.12 with the packages pinned in [`../requirements.txt`](../requirements.txt). These scripts are the design
calculations and the wall-thickness measurement. They read the design data in [`../data/`](../data/) or the published STEP
in [`../cad/`](../cad/). The CAD model itself is published as a file; it is not produced by anything in this folder.

| Script | Role |
|---|---|
| `design_basis.py` | operating point, gas and coolant conditions, velocity triangles at hub, mean and tip, material and design limits; writes `data/design_basis.json` (re-running it reproduces the stored values) |
| `cascade_panel.py` | linear-cascade potential-flow panel method (vortex sheet with the periodic Green's function) used to shape the blade loading |
| `wall_probe.py` | skin and web thickness sampled on the exported solid: `python scripts/wall_probe.py <unzipped STEP>`, about ten minutes |

## Not included

The software behind the other geometry-review results, the cooling model, the 2-D RANS and FEA set-ups and the optimisation
are not published; their results are in [`../verification/`](../verification/README.md), [`../design/`](../design/README.md)
and [`../analysis_context/`](../analysis_context/README.md).
