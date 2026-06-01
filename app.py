import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *

st.set_page_config(layout="wide")
st.title("Von Mises")

# ---------------------------------------
# BASE EXACTA DEL EXCEL
# ---------------------------------------
tubos = {
    "3 1/2 #9.2": (1.75*2, 0.254),
    "3 1/2 #7.7": (1.75*2, 0.216),
    "2 7/8 #6.4": (1.438*2, 0.254),
    "2 7/8 #4.04": (1.44*2, 0.177),
    "5 1/2 #15.5": (2.75*2, 0.275),
    "5 1/2 #10": (2.75*2, 0.231),
    "7 #23": (3.50*2, 0.317),
    "9 5/8 #36": (4.81*2, 0.395),
    "9 5/8 #43.5": (4.81*2, 0.545)
}

# ---------------------------------------
# SIDEBAR
# ---------------------------------------
st.sidebar.title("Inputs")

tubo_sel = st.sidebar.selectbox("Tubo", list(tubos.keys()))

OD, t = tubos[tubo_sel]
ID = OD - 2*t

# Material
grades = {
    "J55": 55,
    "N80": 80,
    "P110": 110,
    "Q125": 125
}
yield_ksi = grades[st.sidebar.selectbox("Grado", grades.keys())]

# Fluidos
rho_int = st.sidebar.number_input("ρ interno [kg/m3]", value=1050.0)
rho_ext = st.sidebar.number_input("ρ externo [kg/m3]", value=1050.0)

fill_int = st.sidebar.slider("Fill interno [-]", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Fill externo [-]", 0.0, 1.0, 1.0)

# Presión
Pint = st.sidebar.number_input("P interna [psi]", value=0.0)
Pext = st.sidebar.number_input("P externa [psi]", value=0.0)

# Mecánico
Torque = st.sidebar.number_input("Torque [lb-ft]", value=0.0)
F_ext = st.sidebar.number_input("Fuerza axial [lbf]", value=0.0)

prof_max = st.sidebar.number_input("Prof [m]", value=3000.0)

# ---------------------------------------
# CALCULO
# ---------------------------------------
sig_ax = []
sig_hoop = []

for i in range(200):

    z = prof_max * i / 200

    Pint_z = presion(z, Pint, rho_int, fill_int)
    Pext_z = presion(z, Pext, rho_ext, fill_ext)

    dP = Pint_z - Pext_z

    s_hoop = tension_circunferencial(dP, OD, t)

    s_ax = tension_axial(
        z, OD, ID,
        rho_int, rho_ext,
        F_ext,
        Pint_z, Pext_z
    )

    sig_ax.append(s_ax)
    sig_hoop.append(s_hoop)

sig_ax = np.array(sig_ax)
sig_hoop = np.array(sig_hoop)

tau = torsion(Torque, OD, ID)

vm = np.sqrt(sig_ax**2 + sig_hoop**2 - sig_ax*sig_hoop + 3*tau**2)

i_crit = np.argmax(vm)

ax_c = sig_ax[i_crit]
hoop_c = sig_hoop[i_crit]

# ---------------------------------------
# ✅ ELIPSE CORRECTA (SIN BUG)
# ---------------------------------------
s = np.linspace(-yield_ksi, yield_ksi, 4000)

yc_top = (s + np.sqrt(4*yield_ksi**2 - 3*s**2)) / 2
yc_bot = (s - np.sqrt(4*yield_ksi**2 - 3*s**2)) / 2

# juntar correctamente
x_vm = np.concatenate([s, s[::-1]])
y_vm = np.concatenate([yc_top, yc_bot[::-1]])

# ---------------------------------------
# PLOT
# ---------------------------------------
fig, ax = plt.subplots(figsize=(7,7))

ax.plot(x_vm, y_vm, color="blue", linewidth=2)

ax.plot(sig_ax, sig_hoop, color="orange", linewidth=2)
ax.scatter(ax_c, hoop_c, color="red", s=120)

lim = yield_ksi * 1.05  # un poco más chico para que no corte

ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

# grilla cada 10 ksi
ticks = np.arange(-yield_ksi, yield_ksi+1, 10)
ax.set_xticks(ticks)
ax.set_yticks(ticks)

ax.grid(True, color="gray", linewidth=0.5)

ax.axhline(0, color="black", linewidth=1.2)
ax.axvline(0, color="black", linewidth=1.2)

# limites
ax.axhline(yield_ksi, color="red", linestyle="--")
ax.axhline(-yield_ksi, color="red", linestyle="--")
ax.axvline(yield_ksi, color="red", linestyle="--")
ax.axvline(-yield_ksi, color="red", linestyle="--")

ax.set_aspect("equal")

ax.set_xlabel("σ axial [ksi]")
ax.set_ylabel("σ circunferencial [ksi]")

st.pyplot(fig)

