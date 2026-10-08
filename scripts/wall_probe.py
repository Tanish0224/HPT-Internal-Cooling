"""Wall / web thickness measured on the EXPORTED solid's own faces. Read-only; extrema distances on the exported solid, no mesh.

Identifies the large periodic B-spline faces of the STEP: the outer airfoil surface (largest, z ~ 253-297.5) and one cavity-wall face per passage
(by chordwise x-range: LE, A1, B1, B2, B3, TE). Random points on each cavity-wall face (vertices of a 0.05 mm tessellation of that face, so they lie
on the trimmed face) are measured to (a) the outer airfoil face = skin wall, and (b) every other cavity-wall face = web / rib-wall ligament.
Reported: min, 1st/5th percentile, median, and the thinnest points. Design values for comparison: skin wall 1.0 mm, web 0.9 mm (design basis).
Limits: only the cavity-wall B-spline faces (not rib sides, pins, hole walls, TE cut-back lips, platform or root); distance to a face is the true
minimum, i.e. a conservative lower bound of the thickness along the normal; hole breakouts lower nothing here because holes are separate faces.
Usage: python wall_probe.py <step>   -> <stem>_wallprobe.json next to the STEP"""
import sys, os, json, time, numpy as np, cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_BSplineSurface
from OCP.gp import gp_Pnt

N_PTS, SEED = 400, 20261005
path = sys.argv[1]; rng = np.random.default_rng(SEED)
sh = cq.importers.importStep(path).val()
big = []
for f in sh.Faces():
    if BRepAdaptor_Surface(f.wrapped).GetType() == GeomAbs_BSplineSurface and f.Area() > 300.0:
        bb = f.BoundingBox()
        if bb.zmin > 245.0: big.append((f.Area(), f, bb))
big.sort(key=lambda t: -t[0])
oml = big[0][1]; print("outer airfoil face: area %.1f z[%.1f,%.1f]" % (big[0][0], big[0][2].zmin, big[0][2].zmax), flush=True)
names = (("LE", -15.0, -10.0), ("A1", -14.5, -5.0), ("B1", -9.0, 1.5), ("B2", -2.5, 6.5), ("B3", 3.5, 10.0), ("TE", 8.0, 17.0))
cav = {}
for area, f, bb in big[1:]:
    cx = 0.5 * (bb.xmin + bb.xmax)
    for nm, lo, hi in names:
        if nm not in cav and lo <= cx <= hi and abs(bb.xmin - lo) < 6 and area > 300:
            cav[nm] = f; print("cavity-wall face %-3s area %7.1f x[%.1f,%.1f] z[%.1f,%.1f]" % (nm, area, bb.xmin, bb.xmax, bb.zmin, bb.zmax), flush=True); break
def dist(p, face):
    e = BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex(), face.wrapped); return e.Value()
rep = dict(file=path, seed=SEED, n_points=N_PTS, faces={}); t0 = time.time()
for nm, f in cav.items():
    v, _ = f.tessellate(0.05, 0.3); V = np.array([[q.x, q.y, q.z] for q in v])
    V = V[(V[:, 2] > 255.0) & (V[:, 2] < 295.5)]            # stay clear of the platform fillet and the tip cap
    P = V[rng.choice(len(V), size=min(N_PTS, len(V)), replace=False)]
    skin = np.array([dist(p, oml) for p in P]); row = dict(area=round(f.Area(), 1), n=int(len(P)),
        skin_wall=dict(min=float(skin.min()), p1=float(np.percentile(skin, 1)), p5=float(np.percentile(skin, 5)), median=float(np.median(skin))), webs={})
    j = int(np.argmin(skin)); row["skin_thinnest"] = dict(d=round(float(skin[j]), 3), p=[round(float(x), 2) for x in P[j]])
    for on, g in cav.items():
        if on == nm: continue
        d = np.array([dist(p, g) for p in P[:150]])
        if d.min() < 3.0: row["webs"][on] = dict(min=float(d.min()), p5=float(np.percentile(d, 5)), median=float(np.median(d)))
    rep["faces"][nm] = row
    print(nm, "skin min %.3f p1 %.3f p5 %.3f med %.3f | webs %s | %.0fs" % (row["skin_wall"]["min"], row["skin_wall"]["p1"], row["skin_wall"]["p5"], row["skin_wall"]["median"],
          {k: round(v["min"], 3) for k, v in row["webs"].items()}, time.time() - t0), flush=True)
json.dump(rep, open(os.path.splitext(path)[0] + "_wallprobe.json", "w"), indent=1)
print("WALL PROBE done %.0fs" % (time.time() - t0), flush=True)
