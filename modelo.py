import numpy as np

# =========================================
# CONVERSIONES
# =========================================
def kgm3_to_lbft3(rho):
    return rho * 0.062428


# =========================================
# GEOMETRIA
# =========================================
def area_metal(OD, ID):
    return np.pi * (OD**2 - ID**2) / 4


# =========================================
# RADIAL + PRESION EXTERNA TOTAL
# =========================================
def external_pressure(Pext_surface, rho_ext, z_ft):
    return Pext_surface + rho_ext * z_ft / 144


def radial_stress(Po):
    return -Po


# =========================================
# HOOP (LAME + thin wall)
# =========================================
def hoop_stress(Pi, Po, OD, ID):

    t = (OD - ID) / 2

    if OD / t >= 20:
        return (Pi - Po) * OD / (2 * t)

    ri = ID / 2
    ro = OD / 2

    A = (Po * ro**2 - Pi * ri**2) / (ro**2 - ri**2)
    B = (ri**2 * ro**2 * (Pi - Po)) / (ro**2 - ri**2)

    return A + B / ri**2


# =========================================
# TORSION
# =========================================
def torsion(T, OD, ID):

    T = T * 12

    ro = OD / 2
    ri = ID / 2

    J = np.pi / 2 * (ro**4 - ri**4)

    return T * ro / J


# =========================================
# AXIAL
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

    A = area_metal(OD, ID)

    A_ext = np.pi * OD**2 / 4
    A_ext_ft2 = A_ext / 144

    # peso
    F_weight = peso_lbft * z_ft

    # flotacion
    F_buoy = rho_ext * fill_ext * z_ft * A_ext_ft2

    F_total = F_weight - F_buoy + F_ext

    sigma_ax = F_total / A

    # extremos cerrados (BIEN)
    if condicion == "Cerrado":

        ri = ID / 2
        ro = OD / 2

        sigma_pressure = (Pi * ri**2 - Po * ro**2) / (ro**2 - ri**2)

        sigma_ax += sigma_pressure

    return sigma_ax


# =========================================
# VON MISES
# =========================================
def von_mises_3d(sa, sh, sr, tau):

    return np.sqrt(
        0.5 * (
            (sa - sh)**2 +
            (sh - sr)**2 +
            (sr - sa)**2
        )
        + 3 * tau**2
    )


# =========================================
# UTILIZACION
# =========================================
def utilization(vm, smys_ksi):
    return vm / (smys_ksi * 1000) * 100


def design_check(vm, smys_ksi):
    return "FAIL" if vm > smys_ksi * 1000 else "PASS"
