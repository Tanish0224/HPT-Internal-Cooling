# Geometry review of the current CAD model

These are geometric reviews of the exported current CAD model. They were carried out on the file whose geometry section is
identical to the published STEP (see [`../cad/README.md`](../cad/README.md)). They show that the solid contains the designed
features and that the passages are connected as designed. They do not show that the design performs: there is no flow,
heat-transfer or structural result for the current design.

**Status words.** VERIFIED: measured on the exported solid. CALCULATED: from the project model or from the intended feature
geometry. ASSUMED: a stated assumption. NOT VERIFIED: not done.

## What was reviewed

| Review | What was examined | Result | Status | Limits | Record |
|---|---|---|---|---|---|
| Solid and topology | one solid, valid, one shell, face count | 1 solid, valid, 1,542 faces | VERIFIED | | `check_summary.json` |
| Volume | adaptive surface integration; independent mesh volume; SolidWorks import | 17,216.6 mm³; mesh 17,308 mm³ (+0.5 %); SolidWorks 17,218.5 mm³ | VERIFIED | a default surface-integration volume gives 16,500.8 mm³ on this model and is not used | `volume_measurement.json`, `solidworks_import.json` |
| Hole breakthrough | each hole's intended volume, shrunk 10 %, intersected with the solid; residual metal measured | all 91 holes: 0.0 mm³ residual metal, so every hole is cut through | VERIFIED | the hole volumes come from the intended hole geometry in the design data | `hole_residual_*.json` |
| Hole ends | a point 0.15 mm beyond each hole end must be outside the metal | all confirmed except SS2 row #7, whose inner end only touches cavity B1; it is accepted because its passage link and residual-metal result confirm it | VERIFIED, one marginal hole | | `check_summary.json` |
| Outlet openings | for the 55 outlets (51 film holes, 4 tip holes), the hole axis crosses the outer surface and one end lies in ambient air | 55 of 55 | indication only | geometric test of the intended hole; it was not shown to reject a closed hole; hole breakthrough itself is the residual-metal review | `film_breakout.json` |
| Connectivity | each feed, hole and passage link overlaps its intended passage; points sampled in the overlap are void | 133 intended links found; both feeds reach the root face; 49 passage pairs have no unintended overlap | CALCULATED on the intended geometry; samples confirmed on the solid | overlaps and isolation compare feature volumes; only the sampled points are classified on the solid; not a flood fill | `connectivity_*.json` |
| Passage interiors | 300 random points per passage must not be metal | 10 passages, 0 metal points | VERIFIED | sampled | `passage_void_*.json` |
| Trailing-edge discharge slots | 15 points along each of the 11 slots must be void | all 11 open from the pin cavity to the outside | VERIFIED | sampled point classification on the solid | `te_exit_path.json` |
| Wall thickness | shortest distance from sampled wall points to the opposite wall | skin minimum 0.677 mm (trailing edge), 0.91 mm (A1), 0.938 mm or more elsewhere; web minimum 0.848 mm | VERIFIED against a 0.457 mm screening floor | 400 samples per skin face, 150 per web; the floor is a patent value | `wall_probe.json` |
| Hole spacing | smallest edge-to-edge gap between neighbouring holes of a family | tip holes 0.72 mm, crossover holes 1.40 mm, jets 1.96 mm, showerhead 2.03 mm | CALCULATED on the intended geometry | not measured on the solid | `connectivity_A_B0_C_F_G.json` (`ligaments`) |
| Design agreement | counts and diameters of the intended holes (design file of 94 holes minus the three removed) | 16 / 20 / 27 / 12 / 12 / 4 = 91 holes; diameters as designed | CALCULATED (consistency with the design data) | not a measurement of the solid | `connectivity_A_B0_C_F_G.json` (`design_check`) |

The overall summary (`check_summary.json`) records every review stage as satisfied against the 0.457 mm wall floor, i.e. the
geometry review completed successfully. Against the 0.76 mm conventional-casting indicator the trailing-edge lip would not
qualify; that is the manufacturing assumption stated in [`../LIMITATIONS.md`](../LIMITATIONS.md).

## What was not reviewed

* Flood-fill connectivity of the whole coolant volume (links and samples were examined, not full voxel connectivity).
* Hole-to-hole interference beyond the spacing above.
* Exit shape and area of film holes (a surface-intersection measurement).
* Flow, pressure drop, heat transfer, temperature, stress or life on the current design (no CFD, CHT or FEA).
* Manufacturability, tolerance or casting yield.
* Why SolidWorks reports `Check2` = 2 for the imported file. The import is one body and the volume agrees; SolidWorks counts 1,551 faces against 1,542 and a bounding box about 1.3 mm wider in both x and y, which was not investigated.
* Independent review.

## About the records

The files in [`results/`](results/) are the recorded outputs of the review, with local file paths replaced by file names; no
other field was changed. Their `sha256` fields refer to the reviewed copy of the file (`4c14c283…`), whose geometry section
is identical to the published STEP.

## What can be re-checked from this repository

* **File identity:** the archive, STEP and geometry-section SHA-256 values, the face counts, bounding box and volumes in
  [`../cad/MANIFEST.json`](../cad/MANIFEST.json) can be compared with the unzipped file in any STEP-capable tool.
* **Wall thickness:** `python scripts/wall_probe.py <unzipped STEP>` repeats the sampled wall measurement (about ten minutes);
  repeated on the published STEP it gave identical values.
* **Everything else** in the table above is recorded in `results/`. The software that produced those records is not
  published, so those results cannot be re-run from this repository, and no claim is made that the CAD model can be
  regenerated here.
