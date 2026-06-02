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
# LAME COMPLETO
# =========================================
def stresses_lame(Pi, Po, OD, ID):

    ri = ID / 2
    ro = OD / 2

    # coeficientes Lamé
    A = (Po * ro**2 - Pi * ri**2) / (ro**2 - ri**2)
    B = (ri**2 * ro**2 * (Pi - Po)) / (ro**2 - ri**2)

    # tensiones en pared interna (ri)
    sigma_r = -Pi                     # radial
    sigma_theta = A + B / ri**2       # hoop

    return sigma_r, sigma_theta


# =========================================
# AXIAL REAL
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

    rho_ext = kgm3_to_lbft3(rho_ext)

    A = area_metal(OD, ID)
    A_ext = np.pi * OD**2 / 4
    A_ext_ft2 = A_ext / 144

    # peso acero
    F_weight = peso_lbft * z_ft

    # flotación externa
    F_buoy = rho_ext * fill_ext * z_ft * A_ext_ft2

    # presión axial
    if modo == "Libre":
        F_pressure = 0
    else:
        A_int = np.pi * ID**2 / 4
        F_pressure = (Pi - Po) * A_int

    F_total = F_weight - F_buoy + F_ext + F_pressure

    return F_total / A


# =========================================
# VON MISES 3D REAL (CLAVE)
# =========================================
def von_mises_3d(sig_ax, sig_hoop, sig_rad):

    return np.sqrt(
        0.5 * (
            (sig_ax - sig_hoop)**2 +
            (sig_hoop - sig_rad)**2 +
            (sig_rad - sig_ax)**2
        )
    )


# =========================================
# UTILIZACION
# =========================================
def utilization(smys_ksi, vm):

    smys = smys_ksi * 1000

    return vm / smys * 100


# =========================================
# CHECK
# =========================================
def design_check(vm, smys_ksi):

    smys = smys_ksi * 1000

    return "FAIL" if vm > smys else "PASS"

