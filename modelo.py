import numpy as np

# ----------------------------------------
# PROPIEDAD ACERO (peso específico)
# ----------------------------------------
rho_steel = 490  # lbf/ft³


# ----------------------------------------
# PRESION (psi)
# ----------------------------------------
def presion(z_ft, P_surface, rho_lbft3, fill):
    # (lbf/ft³ * ft) / 144 -> psi
    return P_surface + (rho_lbft3 * z_ft * fill) / 144


# ----------------------------------------
# LAME (psi)
# ----------------------------------------
def lame(Pi, Po, ri, ro, r):

    A = (Po * ro**2 - Pi * ri**2) / (ro**2 - ri**2)
    B = (ri**2 * ro**2 * (Pi - Po)) / (ro**2 - ri**2)

    sigma_hoop = A + B / r**2
    sigma_rad  = A - B / r**2

    return sigma_hoop, sigma_rad   # psi


# ----------------------------------------
# AXIAL (psi) — CORREGIDO UNIDADES
# ----------------------------------------
def axial(z_ft, OD, ID, rho_int, rho_ext, F_ext, Pint, Pext, modo):

    # áreas en in²
    A_ext = np.pi * OD**2 / 4
    A_int = np.pi * ID**2 / 4
    A     = A_ext - A_int

    # ✅ convertir a ft²
    A_ext_ft2 = A_ext / 144
    A_int_ft2 = A_int / 144
    A_ft2     = A / 144

    # --------------------------------
    # PESO Y FLOTACION (CORRECTOS)
    # --------------------------------
    F_weight = rho_steel * A_ft2 * z_ft

    F_buoy = rho_ext * A_ext_ft2 * z_ft \
           - rho_int * A_int_ft2 * z_ft

    # --------------------------------
    # PRESION AXIAL
    # --------------------------------
    if modo == "Anclado":
        F_pressure = (Pint - Pext) * A_int  # psi*in² = lb
    else:
        F_pressure = 0

    # --------------------------------
    # TOTAL
    # --------------------------------
    F_total = F_weight - F_buoy + F_pressure + F_ext

    sigma = F_total / A  # psi

    return sigma


# ----------------------------------------
# TORSION (psi)
# ----------------------------------------
def torsion(T, OD, ID):

    T = T * 12  # lb-ft → lb-in

    ro = OD / 2
    ri = ID / 2

    J = np.pi/2 * (ro**4 - ri**4)

    tau = T * ro / J

    return tau


# ----------------------------------------
# VON MISES 3D
# ----------------------------------------
def VM(s1, s2, s3, tau):

    return np.sqrt(
        0.5 * ((s1 - s2)**2 +
               (s2 - s3)**2 +
               (s3 - s1)**2)
        + 3 * tau**2
    )

