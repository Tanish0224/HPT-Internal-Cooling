"""
Linear-cascade potential-flow panel method (linear-strength vortex sheet, stream-function
formulation) with the periodic Green's function of an infinite row of vortices:

    psi = -(Gamma / 2 pi) * ln| sinh( pi (z - z0) / s ) |        row spacing s along y

The ln|z - z0| part is integrated analytically over each straight panel; the smooth remainder
ln|sinh(w)/w| by Gauss quadrature. Mean-flow condition: W_my = W1y + Gamma/(2 s), which follows
from the far-field induced velocity of the vortex row (+-Gamma/2s downstream/upstream).
Kutta condition for the rounded trailing edge: equal surface speed at the two tangency points
where the pressure and suction surfaces meet the TE circle.

Used for design iteration only. Compressibility enters through a Karman-Tsien correction of
the incompressible pressure coefficient; the final section is checked with compressible RANS.
"""
import numpy as np

GL_X, GL_W = np.polynomial.legendre.leggauss(12)

def _log_int(P, A, B):
    """Return F0 = int_0^L ln r dt and F1 = int_0^L t ln r dt for points P (M,2), panels A,B (N,2)."""
    d = B - A
    L = np.hypot(d[:, 0], d[:, 1])
    e = d / L[:, None]
    n = np.stack([-e[:, 1], e[:, 0]], axis=1)
    rel = P[:, None, :] - A[None, :, :]
    x0 = (rel * e[None]).sum(-1)
    y0 = (rel * n[None]).sum(-1)
    def I0(u):
        r2 = u * u + y0 * y0
        lnr = 0.5 * np.log(np.maximum(r2, 1e-300))
        safe = np.where(np.abs(y0) > 1e-14, y0, 1.0)
        at = np.where(np.abs(y0) > 1e-14, y0 * np.arctan(u / safe), 0.0)
        return np.where(r2 > 1e-30, u * lnr, 0.0) - u + at
    def I1(u):
        r2 = u * u + y0 * y0
        lnr = 0.5 * np.log(np.maximum(r2, 1e-300))
        return np.where(r2 > 1e-30, 0.5 * r2 * lnr, 0.0) - u * u / 4
    u0, u1 = -x0, L[None, :] - x0
    F0 = I0(u1) - I0(u0)
    F1 = (I1(u1) + x0 * I0(u1)) - (I1(u0) + x0 * I0(u0))
    return F0, F1, L

def _smooth(P, A, B, s):
    """int_panel phi_A(t) g, int_panel phi_B(t) g with g = ln|sinh(w)/w|, w = pi (P - z')/s."""
    t = 0.5 * (GL_X + 1)                                  # (Q,)
    zq = A[:, None, :] + t[None, :, None] * (B - A)[:, None, :]   # (N,Q,2)
    L = np.hypot(*(B - A).T)
    dz = (P[:, None, None, 0] - zq[None, :, :, 0]) + 1j * (P[:, None, None, 1] - zq[None, :, :, 1])
    w = np.pi * dz / s
    small = np.abs(w) < 1e-6
    ratio = np.where(small, 1.0 + w * w / 6, np.sinh(np.where(small, 1.0, w)) / np.where(small, 1.0, w))
    g = np.log(np.abs(ratio))
    wq = 0.5 * GL_W[None, None, :] * L[None, :, None]
    GA = (g * (1 - t)[None, None, :] * wq).sum(-1)
    GB = (g * t[None, None, :] * wq).sum(-1)
    return GA, GB

def solve(contour, pitch, W1, beta1_deg, kutta_idx):
    """contour: (N,2) closed (last != first), counter-clockwise or clockwise.
    kutta_idx: (i_up, i_lo) node indices of the two TE tangency points.
    Returns dict with node speeds (signed along traversal), Gamma, exit angle."""
    Z = np.asarray(contour, float)
    N = len(Z)
    A = Z; B = np.roll(Z, -1, axis=0)
    F0, F1, L = _log_int(Z, A, B)
    GA, GB = _smooth(Z, A, B, pitch)
    c0 = np.log(np.pi / pitch)
    # psi contribution matrices for node unknowns gamma_j (panel j: A=j, B=j+1)
    KA = (F0 - F1 / L[None, :]) + GA + c0 * L[None, :] / 2
    KB = (F1 / L[None, :]) + GB + c0 * L[None, :] / 2
    M = np.zeros((N, N))
    idx = np.arange(N)
    M[:, idx] += KA
    M[:, (idx + 1) % N] += KB
    M *= -1.0 / (2 * np.pi)
    # Gamma = sum over panels of (gA+gB)/2 L  -> row vector
    gvec = np.zeros(N)
    gvec[idx] += L / 2
    gvec[(idx + 1) % N] += L / 2
    b1 = np.radians(beta1_deg)
    Wx, W1y = W1 * np.cos(b1), W1 * np.sin(b1)
    # psi_inf = Wx*y - Wmy*x, Wmy = W1y + Gamma/(2s)
    # equations: M g + (Wx y_i - W1y x_i) - x_i/(2s) * gvec.g - psi0 = 0
    Amat = np.zeros((N + 1, N + 1))
    rhs = np.zeros(N + 1)
    Amat[:N, :N] = M - np.outer(Z[:, 0], gvec) / (2 * pitch)
    Amat[:N, N] = -1.0
    rhs[:N] = -(Wx * Z[:, 1] - W1y * Z[:, 0])
    iu, il = kutta_idx
    Amat[N, iu] = 1.0; Amat[N, il] = 1.0
    sol = np.linalg.solve(Amat, rhs)
    g = sol[:N]
    Gam = gvec @ g
    W2y = W1y + Gam / pitch
    return dict(gamma=g, Gamma=Gam, Wx=Wx, W1y=W1y, W2y=W2y,
                beta2_deg=np.degrees(np.arctan2(W2y, Wx)), W2=np.hypot(Wx, W2y), psi0=sol[N])

def karman_tsien_mach(V_over_V1, M1, gamma=1.3):
    """Incompressible Cp (ref inlet) -> compressible Cp via Karman-Tsien -> isentropic Mach."""
    cp0 = 1 - V_over_V1 ** 2
    b = np.sqrt(1 - M1 ** 2)
    cp = cp0 / (b + M1 ** 2 / (1 + b) * cp0 / 2)
    # isentropic Mach from p/p01: p/p1 = 1 + cp*gamma/2*M1^2
    p01_p1 = (1 + (gamma - 1) / 2 * M1 ** 2) ** (gamma / (gamma - 1))
    p_p1 = 1 + cp * gamma / 2 * M1 ** 2
    ratio = np.clip(p01_p1 / p_p1, 1.0, None)
    return np.sqrt(2 / (gamma - 1) * (ratio ** ((gamma - 1) / gamma) - 1))
