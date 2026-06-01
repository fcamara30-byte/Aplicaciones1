import math

def presion(z, P_surface, rho, fill):
    g = 9.81
    psi_pa = 1 / 6894.76
    return P_surface + rho * g * z * fill * psi_pa


def tension_circunferencial(dP, OD, t):
    return (dP * OD) / (2 * t) / 1000  # ksi


def tension_axial(z, OD, ID, rho_int, rho_ext):
    g = 9.81

    A_ext = math.pi * OD**2 / 4
    A_int = math.pi * ID**2 / 4
    A = A_ext - A_int

    rho_steel = 7850

    masa = A * rho_steel
    buoy = A_ext * rho_ext - A_int * rho_int

    F = (masa - buoy) * g * z
    sigma = F / A

    return sigma / 6894.76 / 1000  # ksi


def torsion(T_lbft, OD, ID):
    T = T_lbft * 12

    ro = OD / 2
    ri = ID / 2

    J = math.pi / 2 * (ro**4 - ri**4)

    tau = T * ro / J

    return tau / 1000  # ksi


def von_mises(sig_ax, sig_hoop, tau):
    return math.sqrt(sig_ax**2 + sig_hoop**2 - sig_ax*sig_hoop + 3*tau**2)
