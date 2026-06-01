import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *

st.set_page_config(layout="wide")
st.title("Diseño Tubing - Von Mises")

# =========================================
# CONVERSIONES
# =========================================
def kgm3_to_lbft3(rho):
    return rho * 0.062428

def m_to_ft(z):
    return z * 3.28084


# =========================================
# BASE TUBOS
# =========================================
tubos = {
    "2 7/8 #6.4": (2.875, 2.441, 6.4),
    "2 7/8 #4.04": (2.875, 2.565, 4.04),
    "3 1/2 #9.2": (3.5, 2.992, 9.2),
    "3 1/2 #7.7": (3.5, 3.068, 7.7),
    "5 1/2 #15.5": (5.5, 4.95, 15.5),
    "5 1/2 #10": (5.5, 5.095, 10),
    "7 #23": (7.0, 6.622, 23),
    "9 5/8 #36": (9.625, 8.921, 36),
    "9 5/8 #43.5": (9.625, 8.681, 43.5)
}

# =========================================
# INPUTS
# =========================================
st.sidebar.title("Inputs")

tubo = st.sidebar.selectbox("Tubing", list(tubos.keys()))
OD, ID, peso = tubos[tubo]

grado = st.sidebar.selectbox("Grado", ["J55","N80","P110","Q125"])
SMYS = {"J55":55,"N80":80,"P110":110,"Q125":125}[grado]

modo = st.sidebar.selectbox("Condición axial", ["Libre","Anclado","Packer"])

Pint = st.sidebar.number_input("P interna [psi]", 5000.0)
Pext = st.sidebar.number_input("P externa [psi]", 0.0)

rho_int = kgm3_to_lbft3(st.sidebar.number_input("ρ interno [kg/m³]",1050.0))
rho_ext = kgm3_to_lbft3(st.sidebar.number_input("ρ externo [kg/m³]",0.0))

fill_int = st.sidebar.slider("Nivel interno [-]", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Nivel externo [-]", 0.0, 1.0, 0.0)

Torque = st.sidebar.number_input("Torque [lb-ft]", 0.0)
F_ext = st.sidebar.number_input("F axial externa [lbf]", 0.0)

depth_ft = m_to_ft(st.sidebar.number_input("Profundidad total [m]",3000.0))

# =========================================
# PERFIL
# =========================================
sig_ax = []
sig_hoop = []
vm_list = []
z_list = []

tau = torsion(Torque, OD, ID)

for i in range(200):

    z = depth_ft * i / 200

    ax = axial_load(
        OD, ID, peso, z,
        rho_int, rho_ext,
        fill_int, fill_ext,
        F_ext,
        Pint, Pext,
        modo
    )

    hoop = hoop_stress(Pint, Pext, OD, ID)

    vm = von_mises(ax, hoop, tau)

    sig_ax.append(ax / 1000)
    sig_hoop.append(hoop / 1000)
    vm_list.append(vm)
    z_list.append(z)

sig_ax = np.array(sig_ax)
sig_hoop = np.array(sig_hoop)
vm_list = np.array(vm_list)
z_list = np.array(z_list)

# =========================================
# PUNTO CRÍTICO
# =========================================
i_crit = np.argmax(vm_list)

sigma_ax = sig_ax[i_crit]
sigma_hoop = sig_hoop[i_crit]
vm_crit = vm_list[i_crit]

z_crit_ft = z_list[i_crit]
z_crit_m = z_crit_ft / 3.28084

# =========================================
# API BURST
# =========================================
t = (OD - ID)/2
burst = burst_api(SMYS, t, OD)

burst_util = (Pint - Pext) / burst * 100

# =========================================
# UTIL
# =========================================
util_vm = utilization(SMYS, vm_crit)

# =========================================
# ELIPSE LIMPIA
# =========================================
sy = SMYS * 0.95   # 👈 achicada visualmente

s = np.linspace(-sy, sy, 2000)

x_vm = []
y_vm = []

for val in s:
    disc = 4*sy**2 - 3*val**2
    if disc >= 0:
        root = np.sqrt(disc)
        x_vm.append(val)
        y_vm.append((val + root)/2)

for val in reversed(s):
    disc = 4*sy**2 - 3*val**2
    if disc >= 0:
        root = np.sqrt(disc)
        x_vm.append(val)
        y_vm.append((val - root)/2)

# =========================================
# PLOT
# =========================================
fig, ax = plt.subplots(figsize=(7,7))

ax.plot(x_vm, y_vm, color="blue", lw=2)

