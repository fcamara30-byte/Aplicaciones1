import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Diseño OCTG - Von Misses")

# =========================================
# CONVERSIONES
# =========================================
def kgm3_to_lbft3(rho):
    return rho * 0.062428

def m_to_ft(z):
    return z * 3.28084

def ft_to_m(z):
    return z / 3.28084

# =========================================
# BASE TUBOS
# =========================================
tubos = {
    "7\" #23": (7.0, 6.622, 23),
    "5 1/2\" #15.5": (5.5, 4.778, 15.5),
    "3 1/2\" #9.2": (3.5, 2.992, 9.2),
    "2 7/8 \" #6.5": (2.875, 2.441, 6.5),
}

# =========================================
# INPUTS
# =========================================
st.sidebar.title("Inputs")

tubo = st.sidebar.selectbox("Tubing", list(tubos.keys()))
OD, ID, peso = tubos[tubo]

perdida_pct = st.sidebar.slider("Pérdida de espesor [%]", 0, 100, 0)
perdida = perdida_pct / 100

t_original = (OD - ID) / 2
t_actual = t_original * (1 - perdida)
ID = OD - 2 * t_actual

grado = st.sidebar.selectbox("Grado", ["J55","N80","P110","Q125"])
SMYS = {"J55":55,"N80":80,"P110":110,"Q125":125}[grado]

P_iny = st.sidebar.number_input("Presión de inyección [psi]", value=2000.0)

rho_int = kgm3_to_lbft3(st.sidebar.number_input("ρ interno [kg/m³]", value=1090.0))

fill_int = st.sidebar.slider("Nivel interno [%]", 0, 100, 100) / 100

depth_m = st.sidebar.number_input("Profundidad [m]", value=3000.0)
depth_ft = m_to_ft(depth_m)

Torque = st.sidebar.number_input("Torque [lb-ft]", value=0.0)

# =========================================
# PERFIL
# =========================================
sig_ax, sig_hoop, vm_list, z_list = [], [], [], []

for i in range(200):

    z = depth_ft * i / 199
    z_int = z * fill_int

    # =========================================
    # PRESION (EXACTA DEL EXCEL)
    # =========================================

    P_hid_ksi = rho_int * z_int / 144 / 1000
    Pi = P_hid_ksi + (P_iny / 1000)

    # =========================================
    # HOOP (EXCEL)
    # =========================================

    t = (OD - ID) / 2
    hoop = Pi * OD / (2 * t)

    # =========================================
    # AXIAL (EXCEL → SOLO PESO)
    # =========================================

    A = np.pi/4 * (OD**2 - ID**2)

    F_weight = peso * z
    sigma_ax = F_weight / A / 1000

    # =========================================
    # RADIAL (EXCEL)
    # =========================================

    sigma_r = -P_hid_ksi

    # =========================================
    # TORSION
    # =========================================

    T = Torque * 12
    ro = OD/2
    ri = ID/2
    J = np.pi/2*(ro**4 - ri**4)
