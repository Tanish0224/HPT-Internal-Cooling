"""
HPT rotor blade -- design basis.

Single source of truth for operating point, gas/coolant conditions, velocity triangles,
material and design limits. Every value carries a status tag:
  ASSUMED     project assumption (with anchor where one exists)
  SOURCED     taken from a cited reference
  CALCULATED  derived here from the above
  DECISION    engineering choice made in this design (reason given)

Reference keys match design/REFERENCES.md. 'E3' = NASA CR-167955 (Halila, Lenahan, Thomas,
GE, 1982), Energy Efficient Engine HPT detailed design report.
"""
import json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "data", "design_basis.json")

# ---------------------------------------------------------------- gas model
GAMMA = 1.30          # ASSUMED, combustion products at ~1600 K (project value retained)
R_GAS = 287.0         # J/kg/K, ASSUMED (project assumption)
CP_GAS = GAMMA * R_GAS / (GAMMA - 1.0)
PR_GAS = 0.70         # ASSUMED (later correction)

def mu_gas(T):
    """Sutherland law for air, used for hot gas (ASSUMED; project practice)."""
    return 1.716e-5 * (T / 273.15) ** 1.5 * (273.15 + 110.4) / (T + 110.4)

def k_gas(T):
    return mu_gas(T) * CP_GAS / PR_GAS

# coolant (air) properties, simple fits adequate for 800-1000 K (ASSUMED)
CP_COOL = 1130.0      # J/kg/K air near 900 K
GAMMA_COOL = 1.35
R_COOL = 287.0
PR_COOL = 0.70

def mu_air(T):
    return 1.716e-5 * (T / 273.15) ** 1.5 * (273.15 + 110.4) / (T + 110.4)

def k_air(T):
    return mu_air(T) * CP_COOL / PR_COOL

# ---------------------------------------------------------------- annulus / speed
R_HUB, R_MEAN, R_TIP = 0.2525, 0.2750, 0.2975   # m, annulus retained from an earlier project stage
U_MEAN = 350.0                                   # m/s ASSUMED (project assumption)
OMEGA = U_MEAN / R_MEAN

# ---------------------------------------------------------------- rotor inlet (NGV exit)
T01 = 1700.0      # K   ASSUMED (project assumption); E3 stage-1 rotor-inlet design T41 = 1421 C = 1694 K
P01 = 3.0e6       # Pa  ASSUMED (project assumption); E3 compressor delivery 2.66-3.08 MPa
C1_MEAN = 600.0   # m/s ASSUMED (project assumption)
ALPHA1_MEAN = 68.0  # deg ASSUMED (project assumption)
ALPHA3_MEAN = -20.0 # deg DECISION: counter-swirl so hub reaction >= 0.2 and mean reaction ~0.32
                    #     (E3 stage 1 reaction 0.34, swirl ~16-17 deg)

# ---------------------------------------------------------------- coolant supply
T3_COMPRESSOR = 866.0   # K  SOURCED/ANCHOR: E3 rotor cooling source 593 C at pitch line (Fig. 20)
P_COMB_RECOVERY = 0.965 # -  ANCHOR: E3 stage-1 nozzle table p3 = 2.66 MPa vs gas PT = 2.57 MPa
R_INDUCER = 0.15        # m  ASSUMED radius at which coolant is brought on board at wheel speed
SUPPLY_LOSS = 0.95      # -  ASSUMED total-pressure retention, inducer -> blade root

def velocity_triangles(r):
    """Free vortex (r*C_theta const), constant Cx through the rotor."""
    U = OMEGA * r
    Cx = C1_MEAN * math.cos(math.radians(ALPHA1_MEAN))
    Ct2 = C1_MEAN * math.sin(math.radians(ALPHA1_MEAN)) * R_MEAN / r
    Ct3 = Cx * math.tan(math.radians(ALPHA3_MEAN)) * R_MEAN / r
    C2 = math.hypot(Cx, Ct2)
    W2t, W3t = Ct2 - U, Ct3 - U
    W2, W3 = math.hypot(Cx, W2t), math.hypot(Cx, W3t)
    beta2 = math.degrees(math.atan2(W2t, Cx))
    beta3 = math.degrees(math.atan2(W3t, Cx))
    dh0 = U * (Ct2 - Ct3)
    # static state at rotor inlet (absolute T01 uniform with radius, ASSUMED)
    T2 = T01 - C2 ** 2 / (2 * CP_GAS)
    P2 = P01 * (T2 / T01) ** (GAMMA / (GAMMA - 1))
    T02rel = T2 + W2 ** 2 / (2 * CP_GAS)
    P02rel = P2 * (T02rel / T2) ** (GAMMA / (GAMMA - 1))
    # rotor exit: rothalpy conserved along the (cylindrical) streamline
    T03rel = T02rel
    T3 = T03rel - W3 ** 2 / (2 * CP_GAS)
    rho2 = P2 / (R_GAS * T2)
    a2, a3 = math.sqrt(GAMMA * R_GAS * T2), math.sqrt(GAMMA * R_GAS * T3)
    return dict(
        r=r, U=U, Cx=Cx, Ct2=Ct2, Ct3=Ct3, C2=C2, W2=W2, W3=W3,
        beta2_deg=beta2, beta3_deg=beta3, turning_deg=beta2 - beta3,
        dh0=dh0, psi=dh0 / U ** 2, phi=Cx / U,
        reaction=(W3 ** 2 - W2 ** 2) / (2 * dh0),
        T2=T2, P2=P2, rho2=rho2, T02rel=T02rel, P02rel=P02rel, T3=T3,
        M2_abs=C2 / a2, M2_rel=W2 / a2, M3_rel=W3 / a3, W3_over_W2=W3 / W2,
        Re_per_m_inlet=rho2 * W2 / mu_gas(T2),
    )

def coolant_supply():
    P3 = P01 / P_COMB_RECOVERY
    U_ind = OMEGA * R_INDUCER
    # brought on board at wheel speed -> W ~ 0, relative total = static
    T_onboard = T3_COMPRESSOR - U_ind ** 2 / (2 * CP_COOL)
    # pumping in rotating disk/cavity to the blade root: rothalpy conservation
    U_root = OMEGA * R_HUB
    T_root_rel = T_onboard + (U_root ** 2 - U_ind ** 2) / (2 * CP_COOL)
    P_root_rel = SUPPLY_LOSS * P3
    return dict(P3=P3, T3=T3_COMPRESSOR, T_onboard=T_onboard,
                Tc_root_rel=T_root_rel, Pc_root_rel=P_root_rel)

# ---------------------------------------------------------------- material and limits
MATERIAL = dict(
    name="Single-crystal Ni superalloy, CMSX-4 / Rene N5 class (DECISION)",
    note="E3 stage 1 used cast Rene 150 (DS); first-generation SX alloys have since become standard [C1]",
    density=8700.0,  # kg/m3 -- placeholder until property source confirmed (see material_props.py)
)
LIMITS = dict(
    T_metal_max_local_K=1357.0,   # ANCHOR: E3 stage-1 blade max coating temperature 1084 C (LE)
    T_metal_bulk_max_K=1226.0,    # ANCHOR: E3 stage-1 pitch-line bulk 953 C at design coolant flow
    coolant_budget_target_pct=3.0,  # ANCHOR: E3 stage-1 blade 2.25 % (Table VII) / 3.3 % (thermal design)
    backflow_margin_min=0.10,     # ASSUMED design margin; E3 tip-LE margin fell to 9 % at reduced supply
)

def build():
    tri = {name: velocity_triangles(r) for name, r in
           (("hub", R_HUB), ("mean", R_MEAN), ("tip", R_TIP))}
    m = tri["mean"]
    area = math.pi * (R_TIP ** 2 - R_HUB ** 2)
    mdot_core = m["rho2"] * m["Cx"] * area
    cool = coolant_supply()
    return dict(
        gas=dict(gamma=GAMMA, R=R_GAS, cp=CP_GAS, Pr=PR_GAS),
        annulus=dict(r_hub=R_HUB, r_mean=R_MEAN, r_tip=R_TIP, span=R_TIP - R_HUB,
                     omega=OMEGA, rpm=OMEGA * 60 / (2 * math.pi)),
        inlet=dict(T01=T01, P01=P01, C1=C1_MEAN, alpha1=ALPHA1_MEAN, alpha3=ALPHA3_MEAN),
        triangles=tri,
        mdot_core=mdot_core,
        coolant=cool,
        material=MATERIAL,
        limits=LIMITS,
        status={
            "T01,P01,C1,alpha1,U_mean": "ASSUMED (project assumption), consistent with E3 T41 1694 K / P3 2.66-3.08 MPa",
            "alpha3": "DECISION -20 deg (reaction)",
            "T3_compressor": "ANCHOR E3 593 C",
            "R_INDUCER,SUPPLY_LOSS": "ASSUMED",
            "limits": "ANCHOR E3 stage-1 blade temperatures",
        },
    )

if __name__ == "__main__":
    b = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(b, open(OUT, "w"), indent=2)
    for k, t in b["triangles"].items():
        print(f"{k:5s} U={t['U']:.1f} b2={t['beta2_deg']:.2f} b3={t['beta3_deg']:.2f} turn={t['turning_deg']:.1f} "
              f"psi={t['psi']:.2f} R={t['reaction']:.2f} M2rel={t['M2_rel']:.3f} M3rel={t['M3_rel']:.3f} "
              f"T02rel={t['T02rel']:.1f} P02rel={t['P02rel']/1e6:.3f}MPa")
    print("mdot_core", round(b["mdot_core"], 2), "kg/s", b["coolant"])
