import numpy as np

# ==============================
# GEOMETRIA
# ==============================
def area_metal(OD, ID):
    return np.pi * (OD**2 - ID**2) / 4


# ==============================
# AXIAL (peso + flotación)
# ==============================
def axial_load(
    OD, ID,
    peso_lbft,
    z_ft,
    rho_ext,
    fill_ext,
    F_ext
):

    A = area_metal(OD, ID)

    # área externa (ft²)
    A_ext = np.pi * OD**2 / 4 / 144

    # peso acero
    Fw = peso_lbft * z_ft

    # flotación SOLO si hay fluido externo
    Fb = rho_ext * fill_ext * z_ft * A_ext

    F_total = Fw - Fb + F_ext

    return F_total / A


# ==============================
# HOOP (DISEÑO REAL - Barlow)
# ==============================
def hoop_stress(Pi, Po, OD, ID):

    t = (OD - ID) / 2

    return (Pi - Po) * OD / (2*t)


# ==============================
# RADIAL (solo presión externa)
# ==============================
def radial_stress(Po):
    return -Po


# ==============================
# TORSION
# ==============================
def torsion(T, OD, ID):

    T = T * 12

    ro = OD / 2
    ri = ID / 2

    J = np.pi / 2 * (ro**4 - ri**4)

    return T * ro / J


# ==============================
# VON MISES
# ==============================
def von_mises_3d(sa, sh, sr, tau):

    return np.sqrt(
        0.5 * (
            (sa - sh)**2 +
            (sh - sr)**2 +
            (sr - sa)**2
        )
        + 3 * tau**2
    )


# ==============================
# UTILIZACION
# ==============================
def utilization(vm, smys_ksi):
    return vm / (smys_ksi * 1000) * 100


def design_check(vm, smys_ksi):
    return "FAIL" if vm > smys_ksi * 1000 else "PASS"
