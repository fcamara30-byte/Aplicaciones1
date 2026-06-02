import numpy as np

# =========================================
# CONVERSION
# =========================================
def kgm3_to_lbft3(rho):
    return rho * 0.062428


# =========================================
# AREA
# =========================================
def area_metal(OD, ID):
    return np.pi * (OD**2 - ID**2) / 4


# =========================================
# LAME (HOOP + RADIAL)
# =========================================
def stresses_lame(Pi, Po, OD, ID):

    ri = ID / 2
    ro = OD / 2

    A = (Po * ro**2 - Pi * ri**2) / (ro**2 - ri**2)
    B = (ri**2 * ro**2 * (Pi - Po)) / (ro**2 - ri**2)

    sigma_r = -Pi                     # radial
    sigma_theta = A + B / ri**2       # hoop

    return sigma_r, sigma_theta


# =========================================
# AXIAL REAL (SOLO MECANICO)
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

    # -----------------------------------
    # SOLO MECANICO (CLAVE)
    # -----------------------------------
    rho_ext = kgm3_to_lbft3(rho_ext)

    A = area_metal(OD, ID)
    A_ext = np.pi * OD**2 / 4
    A_ext_ft2 = A_ext / 144

    F_weight = peso_lbft * z_ft
    F_buoy = rho_ext * fill_ext * z_ft * A_ext_ft2

    if modo == "Libre":
        F_pressure_end = 0
    else:
        A_int = np.pi * ID**2 / 4
        F_pressure_end = (Pi - Po) * A_int

    F_total = F_weight - F_buoy + F_ext + F_pressure_end

    return F_total / A   # ✅ SOLO MECANICO


# =========================================
# TORSION
# =========================================
def torsion(T_lbft, OD, ID):

    T = T_lbft * 12

    ro = OD / 2
    ri = ID / 2

    J = np.pi / 2 * (ro**4 - ri**4)

    return T * ro / J


# =========================================
# VON MISES 3D
# =========================================
def von_mises_3d(sig_ax, sig_hoop, sig_rad, tau):

    return np.sqrt(
        0.5 * (
            (sig_ax - sig_hoop)**2 +
            (sig_hoop - sig_rad)**2 +
            (sig_rad - sig_ax)**2
        )
        + 3 * tau**2
    )


# =========================================
# UTILIZACION (FS = 0.9)
# =========================================
def utilization(vm, smys_ksi):

    smys = smys_ksi * 1000
    allowable = 0.9 * smys

    return vm / allowable * 100


# =========================================
# CHECK
# =========================================
def design_check(vm, smys_ksi):

    smys = smys_ksi * 1000
    allowable = 0.9 * smys

    return "FAIL" if vm > allowable else "PASS"
