import numpy as np

def presion(z, P_surface, rho, fill):
    g = 9.81
    psi_pa = 1 / 6894.76
    return P_surface + rho * g * z * fill * psi_pa


def tension_circunferencial(dP, OD, t):
    return (dP * OD) / (2 * t) / 1000  # ksi


def tension_axial(z, OD, ID, rho_int, rho_ext, F_ext, Pint, Pext):
    g = 9.81

    A_ext = np.pi * OD**2 / 4
    A_int = np.pi * ID**2 / 4
    A = A_ext - A_int

    rho_steel = 7850

    # peso del acero
    F_weight = rho_steel * A * g * z

    # flotación (correcta)
    F_buoy = rho_ext * A_ext * g * z - rho_int * A_int * g * z

    # presión axial (end cap)
    F_pressure = (Pint - Pext) * 6894.76 * A_int

    # total
    F_total = F_weight - F_buoy + F_pressure + F_ext

    sigma = F_total / A

    return sigma / 6894.76 / 1000  # ksi


def torsion(T_lbft, OD, ID):
    T = T_lbft * 12

    ro = OD / 2
    ri = ID / 2

    J = np.pi / 2 * (ro**4 - ri**4)

    tau = T * ro / J

    return tau / 1000


def von_mises(sig_ax, sig_hoop, tau):
    return np.sqrt(sig_ax**2 + sig_hoop**2 - sig_ax*sig_hoop + 3*tau**2)

