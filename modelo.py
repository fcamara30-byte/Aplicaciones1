import numpy as np

# =========================================
# AREA
# =========================================
def area_metal(OD, ID):
    return np.pi/4 * (OD**2 - ID**2)

def area_int(ID):
    return np.pi/4 * ID**2

def area_ext(OD):
    return np.pi/4 * OD**2


# =========================================
# LAME (correcto paredes gruesas)
# =========================================
def stresses_lame(Pi, Po, OD, ID):

    ri = ID / 2
    ro = OD / 2

    A = (Po * ro**2 - Pi * ri**2) / (ro**2 - ri**2)
    B = (ri**2 * ro**2 * (Pi - Po)) / (ro**2 - ri**2)

    sigma_r = -Pi
    sigma_theta = A + B / ri**2

    return sigma_r, sigma_theta


# =========================================
# AXIAL MECANICO
# =========================================
def axial_mechanical(
    OD, ID,
    weight_lbft,
    depth_ft,
    rho_ext,
    fill_ext,
    F_ext
):
    rho_ext = rho_ext * 0.062428

    A = area_metal(OD, ID)
    A_ext_ft2 = area_ext(OD)/144

    Fw = weight_lbft * depth_ft
    Fb = rho_ext * fill_ext * depth_ft * A_ext_ft2

    return (Fw - Fb + F_ext) / A


# =========================================
# AXIAL PRESION (SOLO si realmente cerrado)
# =========================================
def axial_pressure(Pi, Po, OD, ID):

    ri = ID/2
    ro = OD/2

    return (Pi*ri**2 - Po*ro**2)/(ro**2 - ri**2)


# =========================================
# TORSION
# =========================================
def torsion(T_lbft, OD, ID):

    T = T_lbft * 12
    ro = OD/2
    ri = ID/2

    J = np.pi/2*(ro**4 - ri**4)

    return T*ro/J


# =========================================
# VON MISES 3D
# =========================================
def von_mises(sa, sh, sr, tau):

    return np.sqrt(
        0.5*((sa-sh)**2 + (sh-sr)**2 + (sr-sa)**2)
        + 3*tau**2
    )


# =========================================
# CASO COMPLETO CONSISTENTE
# =========================================
def solve_case(
    OD, ID,
    peso, z,
    Pi, Po,
    rho_ext,
    fill_ext,
    F_ext,
    torque,
    condicion   # "Abierto" o "Cerrado"
):

    # --- presión ---
    sr, sh = stresses_lame(Pi, Po, OD, ID)

    # --- axial mecánico ---
    sa = axial_mechanical(
        OD, ID, peso, z,
        rho_ext, fill_ext,
        F_ext
    )

    # 🔴 SOLO si físicamente cerrado (packer real)
    if condicion == "Cerrado":
        sa += axial_pressure(Pi, Po, OD, ID)

    # --- torsión ---
    tau = torsion(torque, OD, ID)

    # --- VM ---
    vm = von_mises(sa, sh, sr, tau)

    return sa, sh, sr, vm
