import numpy as np

# =========================================
# GEOMETRIA
# =========================================
def area_metal(OD, ID):
    return np.pi/4 * (OD**2 - ID**2)

def area_ext(OD):
    return np.pi/4 * OD**2


# =========================================
# LAME (presión)
# =========================================
def stresses_lame(Pi, Po, OD, ID):

    ri = ID/2
    ro = OD/2

    A = (Po*ro**2 - Pi*ri**2)/(ro**2 - ri**2)
    B = (ri**2*ro**2*(Pi-Po))/(ro**2 - ri**2)

    sigma_r = -Pi
    sigma_theta = A + B/ri**2

    return sigma_r, sigma_theta


# =========================================
# AXIAL (COMPATIBLE CON TU APP)
# =========================================
def axial_load(
    OD, ID,
    peso_lbft,
    z_ft,
    rho_int, rho_ext,
    fill_int, fill_ext,
    F_ext,
    Pi, Po,
    modo,
    condicion
):

    rho_ext = rho_ext * 0.062428

    A = area_metal(OD, ID)
    Aext = area_ext(OD) / 144

    Fw = peso_lbft * z_ft
    Fb = rho_ext * fill_ext * z_ft * Aext

    return (Fw - Fb + F_ext) / A


# =========================================
# TORSION (REAL)
# =========================================
def torsion(T_lbft, OD, ID):

    T = T_lbft * 12

    ro = OD/2
    ri = ID/2

    J = np.pi/2 * (ro**4 - ri**4)

    return T * ro / J


# =========================================
# VON MISES
# =========================================
def von_mises_3d(sa, sh, sr, tau):

    return np.sqrt(
        0.5*((sa - sh)**2 +
             (sh - sr)**2 +
             (sr - sa)**2)
        + 3*tau**2
    )


# =========================================
# RESULTADOS
# =========================================
def utilization(vm, smys):

    smys = smys * 1000
    return vm / (0.9 * smys) * 100


def design_check(vm, smys):

    smys = smys * 1000
    return "FAIL" if vm > 0.9*smys else "PASS"
