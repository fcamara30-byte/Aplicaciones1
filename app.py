import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *

st.set_page_config(layout="wide")
st.title("Von Mises")

# ---------------------------------------
# SIDEBAR
# ---------------------------------------
st.sidebar.title("Inputs")

# Tubo
api = {
    "7": {23.0: (7.0, 0.317), 26.0: (7.0, 0.362)}
}

size = st.sidebar.selectbox("OD [in]", api.keys())
weight = st.sidebar.selectbox("Peso [lb/ft]", api[size].keys())

OD, t = api[size][weight]
ID = OD - 2 * t

# Material
yield_ksi = st.sidebar.selectbox("Yield [ksi]", [55, 80, 110])

# Fluidos
rho_int = st.sidebar.number_input("ρ interno [kg/m3]", 0.0, 2000.0, 1050.0)
rho_ext = st.sidebar.number_input("ρ externo [kg/m3]", 0.0, 2000.0, 1050.0)

fill_int = st.sidebar.slider("Fill interno [-]", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Fill externo [-]", 0.0, 1.0, 1.0)

# Presiones
Pint = st.sidebar.number_input("P interna [psi]", 0.0, 10000.0, 0.0)
Pext = st.sidebar.number_input("P externa [psi]", 0.0, 10000.0, 0.0)

# Mecánico
Torque = st.sidebar.number_input("Torque [lb-ft]", 0.0, 100000.0, 0.0)
F_ext = st.sidebar.number_input("Fuerza axial [lbf]", -1e6, 1e6, 0.0)

prof_max = st.sidebar.number_input("Profundidad [m]", 0.0, 10000.0, 3000.0)

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

vm = von_mises(sig_ax, sig_hoop, tau)

ratio = vm / yield_ksi
i_crit = np.argmax(ratio)

ax_c = sig_ax[i_crit]
hoop_c = sig_hoop[i_crit]

# ---------------------------------------
# ELIPSE (CORRECTA Y CERRADA)
# ---------------------------------------
theta = np.linspace(0, 2*np.pi, 2000)

s1 = yield_ksi * np.cos(theta)
s2 = yield_ksi * np.sin(theta)

# transformación VM a (σax , σhoop)
sigma_ax_ellipse = s1
sigma_hoop_ellipse = s2

# ---------------------------------------
# PLOT
# ---------------------------------------
fig, ax = plt.subplots(figsize=(7,7))

ax.plot(sigma_ax_ellipse, sigma_hoop_ellipse,
        color="blue", linewidth=2)

ax.plot(sig_ax, sig_hoop,
        color="orange", linewidth=2)

ax.scatter(ax_c, hoop_c,
           color="red", s=120)

lim = yield_ksi

ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

ax.axhline(0, color="black")
ax.axvline(0, color="black")

ax.axhline(lim, color="red", linestyle="--")
ax.axhline(-lim, color="red", linestyle="--")
ax.axvline(lim, color="red", linestyle="--")
ax.axvline(-lim, color="red", linestyle="--")

ax.set_aspect("equal")

ax.set_xlabel("σ axial [ksi]")
ax.set_ylabel("σ circ [ksi]")

ax.grid()

st.pyplot(fig)

st.metric("VM/Yield", round(float(max(ratio)),3))
