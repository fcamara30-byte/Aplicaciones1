import numpy as np

# =========================================
# AREA METALICA (in²)
# =========================================
def area_metal(OD, ID):
    return np.pi * (OD**2 - ID**2) / 4


# =========================================
# HOOP (psi)
# =========================================
def hoop_stress(Pi, Po, OD, ID):

    t = (OD - ID) / 2

    # criterio corregido
    if OD / t >= 20:
        return (Pi - Po) * OD / (2 * t)

    # LAME (max en ri)
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
# AXIAL (psi) – CORRECTO CON z LOCAL
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

    A = area_metal(OD, ID)

    A_int = np.pi * ID**2 / 4
    A_ext = np.pi * OD**2 / 4

    # ------------------------
    # peso tubing
    # ------------------------
    F_weight = peso_lbft * z_ft

    # ------------------------
    # empuje externo
    # ------------------------
    F_ext_buoy = rho_ext * fill_ext * z_ft * A_ext / 144

    # ------------------------
    # fluido interno
    # ------------------------
    F_int_weight = rho_int * fill_int * z_ft * A_int / 144

    # ------------------------
    # presión axial
    # ------------------------
    if modo == "Libre":
        F_pressure = 0

    elif modo == "Anclado":
        F_pressure = (Pi - Po) * A_int

    elif modo == "Packer":
        F_pressure = (Pi - Po) * A_int

    else:
        F_pressure = 0

    # ------------------------
    # total
    # ------------------------
    F_total = (
        F_weight
        - F_ext_buoy
        + F_int_weight
        + F_pressure
        + F_ext
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
# API BURST (psi)
# =========================================
def burst_api(smys_ksi, t, OD):

    smys = smys_ksi * 1000

    return 0.875 * 2 * smys * t / OD


# =========================================
# UTILIZATION (%)
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
