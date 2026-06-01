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

def ft_to_m(z):
    return z / 3.28084

# =========================================
# BASE TUBOS (CON LIBRAJE)
# =========================================
tubos = {
    "7\" #23": (7.0, 6.622, 23),
    "5 1/2\" #15.5": (5.5, 4.778, 15.5),
    "3 1/2\" #9.2": (3.5, 2.992, 9.2)
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
condicion = st.sidebar.selectbox(
    "Condición tubing",
    ["Abierto", "Cerrado"]
)

P_iny = st.sidebar.number_input("Presión de inyección [psi]", value=0.0)
Pext_surface = st.sidebar.number_input("Presión externa superficial [psi]", value=0.0)

rho_int_si = st.sidebar.number_input("ρ interno [kg/m³]", value=0.0)
rho_ext_si = st.sidebar.number_input("ρ externo [kg/m³]", value=0.0)

rho_int = kgm3_to_lbft3(rho_int_si)
rho_ext = kgm3_to_lbft3(rho_ext_si)

# ✅ % de llenado (como querías)
fill_int = st.sidebar.slider("Nivel interno [%]", 0, 100, 0) / 100
fill_ext = st.sidebar.slider("Nivel externo [%]", 0, 100, 0) / 100

F_ext = st.sidebar.number_input("Fuerza axial externa [lbf]", value=0.0)

depth_m = st.sidebar.number_input("Profundidad [m]", value=3000.0)
depth_ft = m_to_ft(depth_m)

# =========================================
# PERFIL
# =========================================
sig_ax, sig_hoop, vm_list, z_list = [], [], [], []

for i in range(200):

    z = depth_ft * i / 200

    Pi = P_iny + rho_int * fill_int * z / 144
    Po = Pext_surface + rho_ext * fill_ext * z / 144

    ax_val = axial_load(
        OD, ID, peso, z,
        rho_int, rho_ext,
        fill_int, fill_ext,
        F_ext,
        Pi, Po,
        modo,
        condicion
    )

    hoop = hoop_stress(Pi, Po, OD, ID)
    vm = von_mises(ax_val, hoop, 0)

    sig_ax.append(ax_val/1000)
    sig_hoop.append(hoop/1000)
    vm_list.append(vm)
    z_list.append(z)

sig_ax = np.array(sig_ax)
sig_hoop = np.array(sig_hoop)
vm_list = np.array(vm_list)

# =========================================
# PUNTO CRITICO
# =========================================
i_crit = np.argmax(vm_list)

sx = sig_ax[i_crit]
sy_val = sig_hoop[i_crit]
z_crit = ft_to_m(z_list[i_crit])

# =========================================
# ELIPSE (NO TOCAR)
# =========================================
Sy = SMYS

s = np.linspace(-Sy, Sy, 2000)

x_vm = []
y_vm1 = []
y_vm2 = []

for val in s:
    disc = 4*Sy**2 - 3*val**2
    if disc >= 0:
        root = np.sqrt(disc)
        x_vm.append(val)
        y_vm1.append((val + root)/2)
        y_vm2.append((val - root)/2)

# =========================================
# PLOT (INTACTO)
# =========================================
fig, ax = plt.subplots(figsize=(7,7))

ax.plot(x_vm, y_vm1, 'b', lw=2)
ax.plot(x_vm, y_vm2, 'b', lw=2)

ax.plot(sig_ax, sig_hoop, color="orange", lw=2)

ax.scatter(sx, sy_val, color="red", s=150)

ax.axhline(0, color="black", lw=2)
ax.axvline(0, color="black", lw=2)

ax.axhline(SMYS, color="red", ls="--")
ax.axhline(-SMYS, color="red", ls="--")
ax.axvline(SMYS, color="red", ls="--")
ax.axvline(-SMYS, color="red", ls="--")

lim = SMYS * 1.1
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

ax.set_aspect("equal")
ax.grid(True)

ax.set_xlabel("σ axial [ksi]")
ax.set_ylabel("σ hoop [ksi]")

st.pyplot(fig)

# =========================================
# RESULTADOS
# =========================================
st.subheader("Resultados")

c1, c2, c3 = st.columns(3)

c1.metric("σ axial [ksi]", round(sx,2))
c1.metric("σ hoop [ksi]", round(sy_val,2))

c2.metric("Von Mises [ksi]", round(vm_list[i_crit]/1000,2))
c2.metric("Prof crítica [m]", round(z_crit,0))

c3.metric("Utilización [%]", round(utilization(SMYS, vm_list[i_crit]),1))
c3.metric("Estado", design_check(vm_list[i_crit], SMYS))

