import numpy as np

# ----------------------------------------
# AREA METALICA (in²)
# ----------------------------------------
def area_metal(OD, ID):
    return np.pi * (OD**2 - ID**2) / 4


# ----------------------------------------
# TORSION (psi)
# ----------------------------------------
def torsion(T, OD, ID):
    T = T * 12  # lb-ft → lb-in

    ro = OD / 2
    ri = ID / 2

    J = np.pi / 2 * (ro**4 - ri**4)

    tau = T * ro / J

    return tau


# ----------------------------------------
# HOOP (BARLOW) (psi)
# ----------------------------------------
def hoop_barlow(Pi, Po, OD, ID):
    t = (OD - ID) / 2
    return (Pi - Po) * OD / (2 * t)


# ----------------------------------------
# AXIAL COMPLETO (psi)
# ----------------------------------------
def axial_load(OD, ID, peso_lbft, depth_ft, F_ext, Pi, Po, modo):

    A = area_metal(OD, ID)

    # peso total tubing
    F_weight = peso_lbft * depth_ft

    # flotación simple (opcional mejorar luego)
    BF = (65.0 / 490.0)  # ejemplo agua
    F_buoy = F_weight * BF

    # presión axial
    if modo == "Anclado":
        A_int = np.pi * ID**2 / 4
        F_pressure = (Pi - Po) * A_int
    else:
        F_pressure = 0

    F_total = F_weight - F_buoy + F_pressure + F_ext

    return F_total / A


# ----------------------------------------
# VON MISES (psi)
# ----------------------------------------
def von_mises(sig_ax, sig_hoop, tau):
    return np.sqrt(
        sig_ax**2 +
        sig_hoop**2 -
        sig_ax * sig_hoop +
        3 * tau**2
    )


# ----------------------------------------
# FACTOR DE SEGURIDAD
# ----------------------------------------
def safety_factor(smys, vm):
    return smys / vm
