# CAD

## What is authoritative

| | |
|---|---|
| **Current design** | the current CAD model for this project's scope: `GE_EEDP_P01_HPT_Blade_baseline.step.zip` |
| Current-design structural derivative | `GE_EEDP_P01_HPT_Blade_structural_derivative_for_FEA.step.zip`: outer body and passage network only (no holes, ribs, pins or cut-back); a convenience for structural meshing, derived from the current design. It has 3 shells: the outer surface and two enclosed voids, inferred to be the leading-edge and trailing-edge cavities, now reachable only through the removed holes. Its volume (17,219.1 mm³) is 2.6 mm³ above the baseline because the metal added by closing the holes and the cut-back slightly exceeds the rib and pin metal removed |
| Earlier designs | the previous design (same cooling architecture, faceted rib surfaces) is not published as a file; the initial design is kept for context in [`../history/`](../history/README.md) |

Identity, expected counts and SHA-256 values are in [`MANIFEST.json`](MANIFEST.json). `GE_EEDP_P01` in the file names is a project reference code; it does not indicate a GE part, drawing or data.

## Getting and using the file

The STEP files are zipped (88.6 MB → 23.8 MB for the baseline) to keep the repository small.

```
unzip cad/GE_EEDP_P01_HPT_Blade_baseline.step.zip
sha256sum cad/GE_EEDP_P01_HPT_Blade_baseline.step.zip   # compare with archive_sha256 in MANIFEST.json
```

Units are millimetres. The STEP is an AP214 file. It opens as one solid in SolidWorks 2026
(34.3.2). The coordinate system has **z along the span** (root face at z = 218.0 mm, airfoil
tip at 297.5 mm), x axial (leading edge towards −x) and y tangential. Both root feeds open on the root plane z = 218.0 mm.

`MANIFEST.json` lists the hashes, face counts, bounding box and volumes of both files, so the file can be identified and
compared in any CAD or STEP tool. It does not describe the cooling design; see [`../verification/`](../verification/README.md).

The geometry section of the STEP file (everything from the line `DATA;`) is identical to the file on which the geometry
review was carried out (DATA-section hash `40af25a5…`). The header and timestamp lines differ: the published file carries a
rewritten header, so its full-file hash differs from the hash recorded for the reviewed copy (`4c14c283…`). The geometry is the same.

## Model organisation

One solid containing:

* the **airfoil**: lofted outer surface through sections wrapped on cylinders about the engine axis, with a root fillet;
* the **platform** (hub flow-path face at 252.5 mm radius) and a **flared shank** under the hub airfoil;
* a **simplified root** below the shank, a prismatic stand-in for a fir-tree (not a contact geometry);
* **six cavities**, named by chordwise order: LE, A1, B1, B2, B3, TE; two **feed passages** from the root face
  (A1 and B3); a **tip turn** and a **root turn** connecting B3 → B2 → B1;
* **ribs** inside A1, B1, B2, B3 (70 segments), **pins** in the TE cavity (134), 91 **holes**, and 11 **bleed slots**
  through a cut-back at 88 % chord.

Face census: 1,542 faces: 926 planar, 296 cylindrical, 320 B-spline.

## Added platform edge

A periodic platform face carries one added edge (at x = 7 mm) so that SolidWorks reads the correct volume; the geometry is
unchanged. `_structural_derivative` in a file name marks the model without passage features.

## Known mesh-preparation issues

26 faces smaller than 0.001 mm² remain (20 at the trailing-edge bleed-slot ducts). Defeature at 0.01–0.02 mm before
meshing, and re-check the volume afterwards. The 0.40 mm slots and 0.45 mm holes need at least 4–6 cells across them
for a flow mesh.
