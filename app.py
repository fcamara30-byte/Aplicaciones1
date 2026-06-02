import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *

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

# =========================================
# PERDIDA DE ESPESOR
# =========================================
perdida_pct = st.sidebar.slider("Pérdida de espesor [%]", 0, 100, 0)
perdida = perdida_pct / 100

t_original = (OD - ID) / 2
t_actual = t_original * (1 - perdida)
ID = OD - 2 * t_actual

if t_actual <= 0:
    st.sidebar.error("Espesor nulo")

grado = st.sidebar.selectbox("Grado", ["J55","N80","P110","Q125"])
SMYS = {"J55":55,"N80":80,"P110":110,"Q125":125}[grado]

modo = st.sidebar.selectbox("Condición axial", ["Libre","Anclado","Packer"])
condicion = st.sidebar.selectbox("Condición Tubo", ["Abierto", "Cerrado"])

P_iny = st.sidebar.number_input("Presión de inyección [psi]", value=0.0)
Pext_surface = st.sidebar.number_input("Presión externa superficial [psi]", value=0.0)

rho_int = kgm3_to_lbft3(st.sidebar.number_input("ρ interno [kg/m³]", value=1000.0))
rho_ext = kgm3_to_lbft3(st.sidebar.number_input("ρ externo [kg/m³]", value=1000.0))

fill_int = st.sidebar.slider("Nivel interno [%]", 0, 100, 100) / 100
fill_ext = st.sidebar.slider("Nivel externo [%]", 0, 100, 100) / 100

F_ext = st.sidebar.number_input("Fuerza axial externa [lbf]", value=0.0)

# ✅ torque
Torque = st.sidebar.number_input("Torque [lb-ft]", value=0.0)

depth_m = st.sidebar.number_input("Profundidad [m]", value=2000.0)
depth_ft = m_to_ft(depth_m)

# =========================================
# PERFIL
# =========================================
sig_ax, sig_hoop, vm_list, z_list = [], [], [], []

for i in range(200):

    z = depth_ft * i / 200

    Pi = P_iny + rho_int * fill_int * z / 144

    # ✅ CLAVE
    Po = Pext_surface

    ax_val = axial_load(
        OD, ID, peso, z,
        rho_int, rho_ext,
        fill_int, fill_ext,
        F_ext,
        Pi, Po,
        modo,
        condicion
    )

    sigma_r, hoop = stresses_lame(Pi, Po, OD, ID)

    tau = torsion(Torque, OD, ID)

    vm = von_mises_3d(ax_val, hoop, sigma_r, tau)

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
# ELIPSE (SE CONSERVA TU GRAFICO)
# =========================================
Sy = SMYS

s = np.linspace(-Sy, Sy, 2000)

x_vm, y_vm1, y_vm2 = [], [], []

for val in s:
    disc = 4*Sy**2 - 3*val**2
    if disc >= 0:
        root = np.sqrt(disc)
        x_vm.append(val)
        y_vm1.append((val + root)/2)
        y_vm2.append((val - root)/2)

# =========================================
# PLOT (NO TOCADO)
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

c3.metric("Utilización [%]", round(utilization(vm_list[i_crit], SMYS),1))
c3.metric("Estado", design_check(vm_list[i_crit], SMYS))
