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
# HOOP STRESS (psi)
# =========================================
def hoop_stress(Pi, Po, OD, ID):

    t = (OD - ID) / 2

    # Thin wall (Barlow)
    if OD / t >= 20:
        return (Pi - Po) * OD / (2 * t)

    # Thick wall (Lamé)
    ri = ID / 2
    ro = OD / 2

    A = (Po * ro**2 - Pi * ri**2) / (ro**2 - ri**2)
    B = (ri**2 * ro**2 * (Pi - Po)) / (ro**2 - ri**2)

    # Hoop en pared interna
    return A + B / ri**2


# =========================================
# TORSION (psi)
# =========================================
def torsion(T, OD, ID):

    T = T * 12

    ro = OD / 2
    ri = ID / 2

    J = np.pi / 2 * (ro**4 - ri**4)

    return T * ro / J


# =========================================
# AXIAL (MODELO SIMPLE Y CONSISTENTE)
# =========================================
def axial_load(
    OD, ID,
    peso_lbft,
    z_ft,
    rho_int, rho_ext,   # <- se mantiene rho_int para futuro
    fill_int, fill_ext,
    F_ext,
    Pi, Po,
    modo
):

    # convertir densidad externa
    rho_ext = kgm3_to_lbft3(rho_ext)

    # áreas
    A = area_metal(OD, ID)
    A_ext = np.pi * OD**2 / 4
    A_ext_ft2 = A_ext / 144

    # -----------------------------------
    # PESO ACERO
    # -----------------------------------
    F_weight = peso_lbft * z_ft

    # -----------------------------------
    # FLOTACION (simplificada)
    # -----------------------------------
    F_buoy = rho_ext * fill_ext * z_ft * A_ext_ft2

    # -----------------------------------
    # PRESION AXIAL
    # -----------------------------------
    if modo == "Libre":
        F_pressure = 0

    elif modo == "Anclado":
        A_int = np.pi * ID**2 / 4
        F_pressure = (Pi - Po) * A_int

    elif modo == "Packer":
        A_int = np.pi * ID**2 / 4
        F_pressure = (Pi - Po) * A_int

    else:
        F_pressure = 0

    # -----------------------------------
    # TOTAL
    # -----------------------------------
    F_total = (
        F_weight
        - F_buoy
        + F_ext
        + F_pressure
    )

    return F_total / A


# =========================================
# VON MISES (psi)
# =========================================
def von_mises(sig_ax, sig_hoop, tau):

    return np.sqrt(
        sig_ax**2 +
        sig_hoop**2 -
        sig_ax * sig_hoop +
        3 * tau**2
    )


# =========================================
# UTILIZACION (%)
# =========================================
def utilization(smys_ksi, vm):

    smys = smys_ksi * 1000

    return vm / smys * 100


# =========================================
# SAFETY FACTOR
# =========================================
def safety_factor(smys_ksi, vm):

    smys = smys_ksi * 1000

    return smys / vm


# =========================================
# CHECK
# =========================================
def design_check(vm, smys_ksi):

    smys = smys_ksi * 1000

    return "FAIL" if vm > smys else "PASS"

