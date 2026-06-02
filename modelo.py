import numpy as np

# =========================================
# GEOMETRIA
# =========================================
def area_metal(OD, ID):
    return np.pi/4 * (OD**2 - ID**2)

def area_ext(OD):
    return np.pi/4 * OD**2


# =========================================
# HOOP (BARLOW - IGUAL EXCEL)
# =========================================
def hoop_stress(Pi, Po, OD, ID):

    t = (OD - ID)/2

    return (Pi - Po) * OD / (2*t)


# =========================================
# RADIAL (EXCEL)
# σr = - (Pext + ρgz)
# =========================================
def radial_stress(Pext_surface, rho_ext, z_ft):

    rho_ext_lbft3 = rho_ext * 0.062428

    P_hydro = rho_ext_lbft3 * z_ft / 144

    Po_total = Pext_surface + P_hydro

    return -Po_total


# =========================================
# AXIAL (SOLO MECÁNICO - EXACTO EXCEL)
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

    rho_ext_lbft3 = rho_ext * 0.062428

    A = area_metal(OD, ID)
    Aext = area_ext(OD) / 144

    Fw = peso_lbft * z_ft

    Fb = rho_ext_lbft3 * fill_ext * z_ft * Aext

    F_total = Fw - Fb + F_ext

    return F_total / A


# =========================================
# TORSION
# =========================================
def torsion(T_lbft, OD, ID):

    T = T_lbft * 12

    ro = OD/2
    ri = ID/2

    J = np.pi/2 * (ro**4 - ri**4)

    return T * ro / J


# =========================================
# VON MISES (IDENTICO EXCEL)
# =========================================
def von_mises_3d(sa, sh, sr, tau):

    return np.sqrt(
        0.5*((sa - sh)**2 +
             (sh - sr)**2 +
             (sr - sa)**2)
        + 3*tau**2
    )


# =========================================
# UTILIZACION
# =========================================
def utilization(vm, smys):

    smys = smys * 1000
    return vm / (0.9 * smys) * 100


def design_check(vm, smys):

    smys = smys * 1000
    return "FAIL" if vm > 0.9*smys else "PASS"
