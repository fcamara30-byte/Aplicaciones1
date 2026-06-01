import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *

st.set_page_config(layout="wide")

st.title("Von Mises - Tubing")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Inputs")

# API simple
api = {
    "7": {
        23.0: (7.0, 0.317),
        26.0: (7.0, 0.362),
    }
}

size = st.sidebar.selectbox("OD [in]", list(api.keys()))
weight = st.sidebar.selectbox("Peso [lb/ft]", list(api[size].keys()))

OD, t = api[size][weight]
ID = OD - 2 * t

# Material
yield_ksi = st.sidebar.selectbox("Yield [ksi]", [55.0, 80.0, 110.0])

# Fluidos
rho_int = st.sidebar.number_input("Densidad interna [kg/m3]", value=1050.0)
rho_ext = st.sidebar.number_input("Densidad externa [kg/m3]", value=1050.0)

fill_int = st.sidebar.slider("Fill interno [-]", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Fill externo [-]", 0.0, 1.0, 1.0)

# Presiones
Pint = st.sidebar.number_input("P interna [psi]", value=0.0)
Pext = st.sidebar.number_input("P externa [psi]", value=0.0)

# Mecánico
Torque = st.sidebar.number_input("Torque [lb-ft]", value=0.0)
F_ext = st.sidebar.number_input("Fuerza axial externa [lbf]", value=0.0)

prof_max = st.sidebar.number_input("Profundidad [m]", value=3000.0)

# -----------------------------
# CALCULO
# -----------------------------
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

vm = np.sqrt(sig_ax**2 + sig_hoop**2 - sig_ax * sig_hoop + 3 * tau**2)

ratio = vm / yield_ksi

i_crit = np.argmax(ratio)

ax_c = sig_ax[i_crit]
hoop_c = sig_hoop[i_crit]

# -----------------------------
# ✅ ELIPSE VON MISES REAL
# -----------------------------
sigma_ax = np.linspace(-yield_ksi, yield_ksi, 2000)

sigma_top = []
sigma_bot = []

for s in sigma_ax:

    disc = 4 * yield_ksi**2 - 3 * s**2

    if disc >= 0:
        root = np.sqrt(disc)

        sigma_top.append((s + root)/2)
        sigma_bot.append((s - root)/2)
    else:
        sigma_top.append(np.nan)
        sigma_bot.append(np.nan)

# cerrar
x_vm = np.concatenate([sigma_ax, sigma_ax[::-1]])
y_vm = np.concatenate([sigma_top, sigma_bot[::-1]])

# -----------------------------
# PLOT
# -----------------------------
fig, ax = plt.subplots(figsize=(7,7))

ax.plot(x_vm, y_vm, color="blue", linewidth=2)
ax.plot(sig_ax, sig_hoop, color="orange", linewidth=2)
ax.scatter(ax_c, hoop_c, color="red", s=120)

lim = yield_ksi

ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

ax.set_aspect("equal")

ax.axhline(0, color="black")
ax.axvline(0, color="black")

ax.axhline(lim, color="red", linestyle="--")
ax.axhline(-lim, color="red", linestyle="--")
ax.axvline(lim, color="red", linestyle="--")
ax.axvline(-lim, color="red", linestyle="--")

ax.set_xlabel("σ axial [ksi]")
ax.set_ylabel("σ circunferencial [ksi]")

ax.grid()

st.pyplot(fig)

st.metric("VM/Yield", round(float(np.max(ratio)), 3))
