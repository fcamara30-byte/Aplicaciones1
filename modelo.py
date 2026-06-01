import numpy as np

# =========================================
# CONVERSIONES
# =========================================
def kgm3_to_lbft3(rho):
    return rho * 0.062428  # kg/m³ → lb/ft³


# =========================================
# AREA METALICA (in²)
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

    # Tensión hoop en la pared interna
    return A + B / ri**2


# =========================================
# TORSION (psi)
# =========================================
def torsion(T, OD, ID):

    T = T * 12  # lb-ft → lb-in

    ro = OD / 2
    ri = ID / 2

    J = np.pi / 2 * (ro**4 - ri**4)

    return T * ro / J


# =========================================
# AXIAL (CON ABIERTO / CERRADO)
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
    condicion  # "Abierto" o "Cerrado"
):

    # conversion densidades
    rho_int = kgm3_to_lbft3(rho_int)
    rho_ext = kgm3_to_lbft3(rho_ext)

    # áreas
    A = area_metal(OD, ID)
    A_int = np.pi * ID**2 / 4
    A_ext = np.pi * OD**2 / 4

    # pasar a ft²
    A_int_ft2 = A_int / 144
    A_ext_ft2 = A_ext / 144

    # -----------------------------------
    # PESO ACERO
    # -----------------------------------
    F_weight = peso_lbft * z_ft

    # -----------------------------------
    # FLOTACION (EMPUJE EXTERNO)
    # -----------------------------------
    F_buoy = rho_ext * fill_ext * z_ft * A_ext_ft2

    # -----------------------------------
    # FLUIDO INTERNO (SOLO CERRADO)
    # -----------------------------------
    if condicion == "Cerrado":
        F_int = rho_int * fill_int * z_ft * A_int_ft2
    else:
        F_int = 0

    # -----------------------------------
    # PRESION AXIAL (simplificada)
    # -----------------------------------
    if modo == "Libre":
        F_pressure = 0

    elif modo == "Anclado":
        F_pressure = (Pi - Po) * A_int

    elif modo == "Packer":
        F_pressure = (Pi - Po) * A_int  # placeholder

    else:
        F_pressure = 0

    # -----------------------------------
    # FUERZA TOTAL
    # -----------------------------------
    F_total = (
        F_weight
        + F_int
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
# FACTOR DE SEGURIDAD
# =========================================
def safety_factor(smys_ksi, vm):

    smys = smys_ksi * 1000
    return smys / vm


# =========================================
# CHECK FINAL
# =========================================
def design_check(vm, smys_ksi):

    smys = smys_ksi * 1000
    return "FAIL" if vm > smys else "PASS"

