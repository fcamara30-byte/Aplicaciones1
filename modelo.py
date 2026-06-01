
import math

# ---------------------------
# PRESION
# ---------------------------
def presion(z, P_superficie, densidad, fill):
    g = 9.81
    psi_por_pa = 1 / 6894.76
    return P_superficie + (densidad * g * z * fill) * psi_por_pa


# ---------------------------
# TENSION CIRCUNFERENCIAL
# ---------------------------
def tension_circunferencial(DeltaP, OD, t):
    return (DeltaP * OD) / (2 * t) / 1000  # ksi


# ---------------------------
# TENSION AXIAL
# ---------------------------
def tension_axial(z, OD, ID, rho_int, rho_ext):
    g = 9.81

    area_ext = math.pi * (OD**2) / 4
    area_int = math.pi * (ID**2) / 4
    area = area_ext - area_int

    rho_acero = 7850

    masa = area * rho_acero
    empuje = area_ext * rho_ext - area_int * rho_int

    fuerza = (masa - empuje) * g * z
    sigma = fuerza / area

    return sigma / 6894.76 / 1000  # ksi


# ---------------------------
# TORSION (shear stress)
# ---------------------------
def tension_torsion(T_lbft, OD, ID):
    # convertir a lb-in
    T = T_lbft * 12  

    ro = OD / 2
    ri = ID / 2

    J = (math.pi / 2) * (ro**4 - ri**4)

    tau = (T * ro) / J  # psi

    return tau / 1000  # ksi


# ---------------------------
# VON MISES COMPLETO (3D)
# ---------------------------
def von_mises(sig_ax, sig_hoop, tau):
    return math.sqrt(sig_ax**2 + sig_hoop**2 - sig_ax*sig_hoop + 3*tau**2)
``
