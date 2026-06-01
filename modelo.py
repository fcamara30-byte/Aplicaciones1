
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
def tension_circunferencial(DeltaP, OD, ID):
    t = (OD - ID) / 2
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
# VON MISES
# ---------------------------
def von_mises(sig_ax, sig_hoop):
    return math.sqrt(sig_ax**2 + sig_hoop**2 - sig_ax * sig_hoop)
