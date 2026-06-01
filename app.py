import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *

st.set_page_config(layout="wide")
st.title("Tubing Design - Von Mises Operativo")

# ----------------------------------------
# BASE DE TUBOS (COMPLETA)
# ----------------------------------------
tubos = {
    "2 7/8 #6.4": (2.875, 2.441, 6.4),
    "2 7/8 #4.04": (2.875, 2.565, 4.04),
    "3 1/2 #9.2": (3.5, 2.992, 9.2),
    "3 1/2 #7.7": (3.5, 3.068, 7.7),
    "5 1/2 #15.5": (5.5, 4.95, 15.5),
    "5 1/2 #10": (5.5, 5.095, 10),
    "7 #23": (7.0, 6.366, 23),
    "9 5/8 #36": (9.625, 8.921, 36),
    "9 5/8 #43.5": (9.625, 8.681, 43.5)
}

# ----------------------------------------
# INPUTS
# ----------------------------------------
st.sidebar.title("Inputs")

tubo = st.sidebar.selectbox("Tubing", list(tubos.keys()))
OD, ID, peso = tubos[tubo]

grado = st.sidebar.selectbox("Grado", ["J55","N80","P110","Q125"])
SMYS = {"J55":55000, "N80":80000, "P110":110000, "Q125":125000}[grado]

modo = st.sidebar.selectbox("Condición axial", ["Libre","Anclado"])

Pint = st.sidebar.number_input("P interna [psi]", value=5000.0)
Pext = st.sidebar.number_input("P externa [psi]", value=0.0)

Torque = st.sidebar.number_input("Torque [lb-ft]", value=0.0)
F_ext = st.sidebar.number_input("F axial externa [lbf]", value=0.0)

depth = st.sidebar.number_input("Profundidad [ft]", value=10000.0)

# ----------------------------------------
# CALCULO
# ----------------------------------------
sigma_ax = axial_load(OD, ID, peso, depth, F_ext, Pint, Pext, modo)
sigma_hoop = hoop_barlow(Pint, Pext, OD, ID)
tau = torsion(Torque, OD, ID)

vm = von_mises(sigma_ax, sigma_hoop, tau)
sf = safety_factor(SMYS, vm)

# pasar a ksi
ax_k = sigma_ax / 1000
hoop_k = sigma_hoop / 1000
vm_k = vm / 1000

# ----------------------------------------
# ELIPSE VON MISES
# ----------------------------------------
sy = SMYS / 1000
s = np.linspace(-sy, sy, 2000)

valid_x = []
y_top = []
y_bot = []

for val in s:
    disc = 4*sy**2 - 3*val**2
    if disc >= 0:
        root = np.sqrt(disc)
        valid_x.append(val)
        y_top.append((val + root)/2)
        y_bot.append((val - root)/2)

x_vm = np.array(valid_x + valid_x[::-1])
y_vm = np.array(y_top + y_bot[::-1])

# ----------------------------------------
# PLOT
# ----------------------------------------
fig, ax = plt.subplots(figsize=(7,7))

# elipse
ax.plot(x_vm, y_vm, color="blue", lw=2)

# punto operativo
ax.scatter(ax_k, hoop_k, color="red", s=120)

# ejes
ax.axhline(0, color='black')
ax.axvline(0, color='black')

# escala
lim = sy * 1.1
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

# grilla
ticks = np.arange(-sy, sy+1, 10)
ax.set_xticks(ticks)
ax.set_yticks(ticks)
ax.grid(True)

ax.set_aspect("equal")
ax.set_xlabel("σ axial [ksi]")
ax.set_ylabel("σ hoop [ksi]")

st.pyplot(fig)

# ----------------------------------------
# RESULTADOS
# ----------------------------------------
st.metric("σ axial [ksi]", round(ax_k,2))
st.metric("σ hoop [ksi]", round(hoop_k,2))
st.metric("Von Mises [ksi]", round(vm_k,2))
st.metric("Safety Factor", round(sf,2))

