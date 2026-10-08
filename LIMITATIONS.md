# Limitations

## Scope

1. **No simulation of the current design.** No CFD, conjugate heat-transfer (CHT) or structural analysis has been run on the current design
   geometry, and nothing here is validated by experiment. The current design is a CAD baseline prepared for such work, not a
   production blade.
2. **The operating point is assumed.** The gas state, blade speed and coolant supply are project assumptions anchored
   to a published test-engine design (NASA CR-167955); they are not data of any engine in service.
3. **No manufacturing qualification.** No manufacturer's capability, tolerance or yield was established.

## Model-derived numbers (CALCULATED)

4. **Temperatures, flows and margins are project-model values.** They come from a quasi-3D conduction model coupled to a
   one-dimensional coolant network, with external boundary conditions from 2-D RANS on earlier geometry. They were not
   computed on the current design and have no experimental check.
5. **Several correlations are used outside their range.** Leading-edge jet Reynolds number is about 42,000 against a
   correlation range of 3,000–15,000; film effectiveness uses a flat-plate correlation for shaped holes and
   extrapolates it to cylindrical showerhead holes; the film correlation assumes 30° injection while the modelled suction-side holes
   are inclined at 35–45° (the first feasible angle among 30°, 35°, 40° and 45° was used; the chosen angles are not published); rib enhancement (2.4) and the metal conductivity law are assumed. The sensitivities in
   [`design/sensitivity/`](design/sensitivity/) bound some of this: film effectiveness −30 % adds 46 K, cut-back
   effectiveness 0.7 → 0.5 adds 47 K, internal heat transfer −20 % adds 6 K. These sensitivities were computed on the 94-hole model (nominal 1,312 K, margin 45 K) and were not rerun for 91 holes; if the +46 K and +47 K deltas carry over, either film case alone uses the 40 K margin of the 91-hole design.
6. **The effect of removing three holes is a bound, not a result.** Going from 94 to 91 hole features is modelled with a
   smeared hole density: the two showerhead holes give +5.5 K peak metal temperature and −0.3 g/s coolant, the crossover hole
   0 K and −0.2 g/s (−0.5 g/s together). The local effect at the hub end was not resolved.

## Geometry review

7. **Wall minimum is not sourced to a standard.** The 0.457 mm floor used in the geometry review is the thinnest cast wall in one
   patent (US 5,296,308). A second patent (US 6,255,000) states that conventional casting could not reliably produce
   walls below 0.03 in (0.76 mm). The sampled trailing-edge lip minimum is 0.677 mm (designed 0.75 mm), so the lip assumes an
   advanced thin-wall casting process. The 0.40 mm bleed-slot height is an assumed minimum core thickness. Holes are assumed
   to be drilled or EDM-formed after casting.
8. **Wall values are sampled.** The wall probe uses 400 random points per skin face (150 per web) with a fixed seed; the
   minima are minima of the samples, not of the whole surface. Web minimum 0.848 mm against a 0.9 mm design value.
9. **Several reviews compare the solid with the intended feature geometry.** The hole-breakthrough, passage, connectivity and
   hole-spacing results compare the exported solid with the intended hole and passage geometry taken from the design
   data. They show that the solid contains the designed features, not that the design is correct; a shared error in that
   intended geometry would not be visible to them. Only the sampled-point, residual-metal, wall-thickness and slot reviews
   measure or classify the solid alone.
10. **The outlet-opening review is an indication only.** For the 55 outlets (51 film holes and 4 tip holes) it tests whether
    the hole axis crosses the outer surface and its end lies in air; it was not shown to reject a closed hole. Hole
    breakthrough itself is established by the residual-metal measurement.
11. **Not done:** flood-fill connectivity of the coolant volume; hole-to-hole interference; surface-intersection
    measurement of film-hole exit shapes. One hole (SS2 row #7) reaches its passage with a marginal inner end.
12. **SolidWorks `Check2` returns 2 for the imported file**, a result that has not been explained. The import itself is
    one body with a volume that agrees with the independent measurement. SolidWorks reports 1,551 faces against 1,542 in the STEP file (it splits
    some closed faces) and a bounding box about 1.3 mm wider in both x and y; neither difference was investigated.
13. **Mesh preparation is needed.** 26 faces smaller than 0.001 mm² remain, 20 of them at the junctions of the
    trailing-edge bleed-slot ducts with the cut-back. The ducts sit 0.03 mm off neighbouring faces. Defeaturing at about 0.01–0.02 mm is expected before meshing. An automatic
    small-face fixer made the solid invalid on an earlier model and was not used.
14. **Rib surfaces are approximations.** The current-design ribs are splines through at most 12 points of the original offset curves;
    total rib volume is 0.7–0.9 % below the faceted version, and metal inside the passages is unchanged within 0.1 %.
15. **Volume.** A default surface-integration volume is unreliable on this model (16,500.8 mm³ against 17,216.6 mm³
    from adaptive integration); only the adaptive value and the SolidWorks value are quoted. A periodic platform face carries one added
    edge (at x = 7 mm) so that SolidWorks reads the correct volume; the geometry is unchanged.
16. **The structural derivative is a convenience.** It removes holes, ribs, pins and the cut-back; their local effect is
    neither included nor estimated.

## Earlier-geometry analyses

17. The 2-D RANS and screening FEA in [`analysis_context/`](analysis_context/README.md) were run on earlier geometry (the second design,
    including its flared-shank refinement). They do not validate the current design. The FEA excludes holes, ribs and pins, uses assumed temperature-dependent
    moduli, treats the single crystal as isotropic, and does not model the fir-tree contact or evaluate fatigue.

## Evidence that can and cannot be re-checked

18. The CAD model is published as a file, not with the means to regenerate it. File identity can be compared with the hashes
    in `cad/MANIFEST.json`, and the wall-thickness measurement can be repeated with `scripts/wall_probe.py`. The other
    geometry-review results are recorded in `verification/results/`; the software that produced them is not published, so
    they cannot be re-run here. The cooling model, optimisation, RANS and FEA set-ups are also not published.

This repository has not undergone independent external review.
