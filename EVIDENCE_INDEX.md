# Evidence index

Where each number and claim in this repository comes from.

**Evidence classes**

| Class | Meaning |
|---|---|
| **VERIFIED** | measured on the exported current CAD model, with a recorded result file |
| **SIMULATION** | CFD or FEA result on earlier geometry (second design), never on the current design |
| **CALCULATED** | derived by the project's models or from the intended feature geometry; not CFD or FEA on the current design |
| **SOURCED** | taken from a public document cited in [`design/REFERENCES.md`](design/REFERENCES.md), compared with the source text |
| **ASSUMED / DECISION** | a project assumption or design choice |
| **HISTORICAL** | superseded geometry or an earlier statement, kept for the record |

"Result files" are in [`verification/results/`](verification/results/). Paths in them were rewritten to file names; see
[`verification/README.md`](verification/README.md).

## Design

| Claim | Class | Evidence |
|---|---|---|
| Reference-engine rotor inlet 1,421 °C, delivery pressure 2.66–3.08 MPa, cooling-air source 593 °C, coating maximum 1,084 °C, bulk 953 °C, film holes 0.51 mm, 11 pressure-side bleed slots, 18,000 h life | SOURCED | NASA CR-167955 ([`design/REFERENCES.md`](design/REFERENCES.md), G1) |
| Cast walls 0.018–0.055 in; cores under 0.03 in crushed in conventional casting | SOURCED | US 5,296,308; US 6,255,000 ([`design/REFERENCES.md`](design/REFERENCES.md)) |
| Operating point, blade speed, coolant supply, metal limits | ASSUMED, anchored to the above | [`design/README.md`](design/README.md), [`data/design_basis.json`](data/design_basis.json) |
| Section dimensions, 66 blades, velocity triangles | CALCULATED / DECISION | [`data/blade_sections.json`](data/blade_sections.json), [`data/design_basis.json`](data/design_basis.json), `scripts/design_basis.py` |
| Hole counts, diameters, slot height, wall and web values | DECISION | [`data/cooling_design.json`](data/cooling_design.json); the 91 intended holes in `connectivity_A_B0_C_F_G.json` (`design_check`); the removal of three of the original 94 holes is explained in [`design/README.md`](design/README.md#from-94-to-91-hole-features) |
| Coolant 38.1 g/s (3.15 %), peak metal 1,317 K, bulk 1,151 K, 91 holes | CALCULATED | [`design/sensitivity/hole_removal_sensitivity.json`](design/sensitivity/hole_removal_sensitivity.json) (`filtered_91holes`) |
| Coolant 38.6 g/s (3.19 %), peak metal 1,312 K, back-flow margin 0.112, 94 holes | CALCULATED | [`design/sensitivity/cooling_sensitivity.json`](design/sensitivity/cooling_sensitivity.json) (`nominal`) |
| Removing the showerhead holes: +5.5 K, −0.3 g/s; removing the crossover hole: 0 K, −0.2 g/s (together +5.5 K, −0.5 g/s) | CALCULATED | [`design/sensitivity/hole_removal_sensitivity.json`](design/sensitivity/hole_removal_sensitivity.json) (`bound_showerhead_only`, `bound_crossover_only`) |
| Film −30 % +46 K; cut-back 0.7 → 0.5 +47 K; internal h −20 % +6 K; conductivity +3 / −2 K; leading-edge h −30 % −1 K | CALCULATED | [`design/sensitivity/cooling_sensitivity.json`](design/sensitivity/cooling_sensitivity.json) |
| Trailing-edge lip 0.75 / 0.80 / 0.85 mm changes peak metal temperature by about 0.5 K | CALCULATED | [`design/sensitivity/lip_thickness_sensitivity.json`](design/sensitivity/lip_thickness_sensitivity.json) |
| Design iterations (coolant fraction and peak metal temperature) | CALCULATED (model output; only the chart is published) | [`figures/05_design_iterations.png`](figures/05_design_iterations.png); not regenerable from this repository |
| Reasons for each major decision | DECISION | [`design/decisions.md`](design/decisions.md) |

## Geometry and geometry review (current design)

| Claim | Class | Evidence | Method |
|---|---|---|---|
| One valid solid, 1,542 faces; 926 plane, 296 cylinder, 320 B-spline | VERIFIED | `check_summary.json` (S1), [`cad/MANIFEST.json`](cad/MANIFEST.json) | import of the exported file |
| Volume 17,216.6 mm³ (adaptive integration), 17,218.5 mm³ (SolidWorks 34.3.2) | VERIFIED | `volume_measurement.json`, `solidworks_import.json` | adaptive integration; SolidWorks `LoadFile2` |
| SolidWorks `Check2` = 2, not explained | VERIFIED (as a result) | `solidworks_import.json` | SolidWorks API |
| 91 holes, residual metal 0.0 mm³ in every hole | VERIFIED | `hole_residual_LE_TEcrossover_showerhead.json` (63), `hole_residual_SSrow_SS2row_tipholes.json` (28) | hole volume shrunk 10 %, intersected with the solid |
| 55 of 55 outlets (51 film holes, 4 tip holes) open to ambient | indication only | `film_breakout.json` | axis and end-point classification; not shown to reject a closed hole |
| 11 of 11 bleed-slot ducts open | VERIFIED | `te_exit_path.json` | 15 points per slot classified against the solid |
| 133 intended links; both feeds reach z = 218 mm; 49 isolation pairs without unintended overlap; hole spacing 0.72 mm and up | CALCULATED on the intended geometry, sampled on the solid | `connectivity_*.json`, `check_summary.json` (S2) | overlap volumes and sampled points |
| 10 passages, 300 sampled points each, none metal | VERIFIED | `passage_void_*.json` | point classification |
| Skin minimum 0.677 mm (TE), 0.91 mm (A1), 0.938 mm or more elsewhere; web minimum 0.848 mm | VERIFIED (sampled) | `wall_probe.json`, `check_summary.json` (S4) | extrema distance, 400 / 150 samples |
| 26 faces under 0.001 mm², 61 under 0.01 mm² | VERIFIED | `face_census.json` | face areas of the published file |
| 3,846 → 1,542 faces; B-spline faces 2,624 → 320; rib solid 82 → 6 faces | VERIFIED (previous design file not published) | [`cad/MANIFEST.json`](cad/MANIFEST.json) (hash of the previous design file); [`design/decisions.md`](design/decisions.md) | face counts of the previous and current design files |
| Geometry section of the published STEP identical to the reviewed copy | VERIFIED | [`cad/MANIFEST.json`](cad/MANIFEST.json) (`data_section_sha256`) | hash of the STEP text from `DATA;` |
| Wall-thickness measurement repeated on the published STEP | VERIFIED | `wall_probe.json`, `scripts/wall_probe.py` | the same sampled measurement run again on the published STEP gave identical values |
| The three removed holes and why | CALCULATED from the hole geometry; the solid then measured | [`design/README.md`](design/README.md#from-94-to-91-hole-features) | inner-end position against the cavity floor and tip turn |

## Earlier geometry (not the current design)

| Claim | Class | Evidence |
|---|---|---|
| 2-D RANS exit angle, exit Mach, loss Y at hub, mean, tip | SIMULATION, earlier geometry | [`analysis_context/rans_2d/cascade_performance.json`](analysis_context/rans_2d/cascade_performance.json) |
| Model against RANS external heat transfer | SIMULATION, earlier geometry | [`analysis_context/rans_2d/`](analysis_context/rans_2d/) |
| Screening FEA stresses, creep and modal frequencies, second design (box shank and flared shank) | SIMULATION, earlier geometry | [`analysis_context/fea_screening/`](analysis_context/fea_screening/) |
| Initial-design geometry (231 features, 65 cut features, 29,653.63 mm³), thickness/chord 0.309–0.329, wedge leading edge | HISTORICAL; read from the SolidWorks file and the earlier repository, not regenerable here | [`history/initial_design/`](history/initial_design/README.md) |
