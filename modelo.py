import numpy as np

# AREA
def area_metal(OD, ID):
    return np.pi/4 * (OD**2 - ID**2)

def area_ext(OD):
    return np.pi/4 * OD**2


# LAME
def stresses_lame(Pi, Po, OD, ID):

    ri = ID / 2
    ro = OD / 2

    A = (Po * ro**2 - Pi * ri**2) / (ro**2 - ri**2)
    B = (ri**2 * ro**2 * (Pi - Po)) / (ro**2 - ri**2)

    sigma_r = -Pi
    sigma_theta = A + B / ri**2

    return sigma_r, sigma_theta


# AXIAL
def axial_load(
    OD, ID,
    weight_lbft,
    depth_ft,
    rho_ext,
    fill_ext,
    F_ext
):

    rho_ext = rho_ext * 0.062428

    A = area_metal(OD, ID)
    Aext = area_ext(OD) / 144

    Fw = weight_lbft * depth_ft
    Fb = rho_ext * fill_ext * depth_ft * Aext

    return (Fw - Fb + F_ext) / A


# TORSION
def torsion(T_lbft, OD, ID):

    T = T_lbft * 12
    ro = OD / 2
    ri = ID / 2

    J = np.pi / 2 * (ro**4 - ri**4)

    return T * ro / J


# VON MISES
def von_mises(sa, sh, sr, tau):

    return np.sqrt(
        0.5 * ((sa - sh)**2 + (sh - sr)**2 + (sr - sa)**2)
        + 3 * tau**2
    )


# UTILIZACION
def utilization(vm, smys):

    smys = smys * 1000
    return vm / (0.9 * smys) * 100


def design_check(vm, smys):

    smys = smys * 1000
    return "FAIL" if vm > 0.9 * smys else "PASS"
