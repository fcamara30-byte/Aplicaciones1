import numpy as np

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

    # thin wall (Barlow)
    if OD / t >= 20:
        return (Pi - Po) * OD / (2 * t)

    # thick wall (Lamé)
    ri = ID / 2
    ro = OD / 2

    A = (Po * ro**2 - Pi * ri**2) / (ro**2 - ri**2)
    B = (ri**2 * ro**2 * (Pi - Po)) / (ro**2 - ri**2)

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
# AXIAL CORREGIDO (FISICAMENTE CONSISTENTE)
# =========================================
def axial_load(
    OD, ID,
    peso_lbft,
    z_ft,
    rho_int, rho_ext,
    fill_int, fill_ext,
    F_ext,
    Pi, Po,
    modo
):

    # área metálica
    A = area_metal(OD, ID)

    # -----------------------------------
    # PESO TOTAL DEL ACERO
    # -----------------------------------
    F_weight = peso_lbft * z_ft

    # -----------------------------------
    # FLOTACION CORRECTA
    # basada en volumen de acero
    # -----------------------------------
    rho_mix = rho_ext * fill_ext - rho_int * fill_int

    F_buoy = rho_mix * z_ft * A / 144

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
    # FUERZA TOTAL
    # -----------------------------------
    F_total = F_weight - F_buoy + F_ext + F_pressure

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
# SAFETY FACTOR
# =========================================
def safety_factor(smys_ksi, vm):

    smys = smys_ksi * 1000

    return smys / vm


# =========================================
# UTILIZACION (%)
# =========================================
def utilization(smys_ksi, vm):

    smys = smys_ksi * 1000

    return vm / smys * 100


# =========================================
# CHECK
# =========================================
def design_check(vm, smys_ksi):

    smys = smys_ksi * 1000

    if vm > smys:
        return "FAIL"
    return "PASS"

