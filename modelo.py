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

    # peso real del acero
    sigma_weight = (rho_steel * g * z) / 6894.76 / 1000

    # flotación CORRECTA
    sigma_buoy = ((rho_ext - rho_int) * g * z) / 6894.76 / 1000

    # presión axial (end-cap)
    sigma_pressure = (Pint - Pext) * (A_int / A) / 1000

    # fuerza externa axial
    sigma_ext = F_ext / A / 6894.76 / 1000

    return sigma_weight - sigma_buoy + sigma_pressure + sigma_ext


def torsion(T_lbft, OD, ID):
    T = T_lbft * 12

    ro = OD / 2
    ri = ID / 2

    J = np.pi / 2 * (ro**4 - ri**4)

    tau = T * ro / J

    return tau / 1000


def von_mises(sig_ax, sig_hoop, tau):
    return np.sqrt(sig_ax**2 + sig_hoop**2 - sig_ax*sig_hoop + 3*tau**2)
