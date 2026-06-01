import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *

st.set_page_config(layout="wide")

st.title("Modelo Von Mises – Tubing")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Configuración")

# -------- MODO --------
modo = st.sidebar.radio("Modo", ["API", "Custom"])

# -------- BASE API COMPLETA --------
api = {
    "2 7/8": {
        6.4: (2.875, 0.217),
        8.6: (2.875, 0.276)
    },
    "3 1/2": {
        9.3: (3.5, 0.254),
        12.95: (3.5, 0.318)
    },
    "4 1/2": {
        11.6: (4.5, 0.237),
        15.1: (4.5, 0.337)
    },
    "5 1/2": {
        17.0: (5.5, 0.304),
        20.0: (5.5, 0.361)
    },
    "7": {
        26.0: (7.0, 0.362),
        29.0: (7.0, 0.408),
        32.0: (7.0, 0.453)
    },
    "9 5/8": {
        40.0: (9.625, 0.395),
        47.0: (9.625, 0.472),
        53.5: (9.625, 0.545)
    }
}

# -------- TUBO --------
st.sidebar.subheader("Tubing")

if modo == "API":
    size = st.sidebar.selectbox("OD", list(api.keys()))
    weight = st.sidebar.selectbox("lb/ft", list(api[size].keys()))

    OD, t = api[size][weight]
    ID = OD - 2*t

else:
    OD = st.sidebar.number_input("OD (in)", value=3.5)
    weight = st.sidebar.number_input("lb/ft", value=10.0)

    # aproximación
    t = weight / (10.69 * OD)
    ID = OD - 2*t

st.sidebar.markdown(f"""
### Geometría
- OD: {round(OD,3)} in  
- ID: {round(ID,3)} in  
- t: {round(t,3)} in  
""")

# -------- MATERIAL --------
st.sidebar.subheader("Material")

grades = {
    "J55": 55,
    "N80": 80,
    "P110": 110
}

grado = st.sidebar.selectbox("Grado", list(grades.keys()))
yield_ksi = grades[grado]

# -------- FLUIDOS --------
st.sidebar.subheader("Fluidos")

rho_int = st.sidebar.number_input("ρ interno", value=1050)
rho_ext = st.sidebar.number_input("ρ externo", value=1200)

fill_int = st.sidebar.slider("Fill interno", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Fill externo", 0.0, 1.0, 1.0)

# -------- PRESIONES --------
st.sidebar.subheader("Presiones")

Pint = st.sidebar.number_input("P interna (psi)", value=1500.0)
Pext = st.sidebar.number_input("P externa (psi)", value=0.0)

# -------- MECÁNICO --------
st.sidebar.subheader("Mecánico")

Torque = st.sidebar.number_input("Torque (lb-ft)", value=0.0)
prof_max = st.sidebar.number_input("Profundidad (m)", value=2000)

# -----------------------------
# CALCULO
# -----------------------------
sig_ax = []
sig_hoop = []

for i in range(100):
    z = prof_max * i / 100

    Pint_z = presion(z, Pint, rho_int, fill_int)
    Pext_z = presion(z, Pext, rho_ext, fill_ext)

    dP = Pint_z - Pext_z

    s_hoop = tension_circunferencial(dP, OD, t)
    s_ax = tension_axial(z, OD, ID, rho_int, rho_ext)

    sig_ax.append(s_ax)
    sig_hoop.append(s_hoop)

sig_ax = np.array(sig_ax)
sig_hoop = np.array(sig_hoop)

tau = torsion(Torque, OD, ID)

vm = np.sqrt(sig_ax**2 + sig_hoop**2 - sig_ax*sig_hoop + 3*tau**2)
ratio = vm / yield_ksi

i_crit = np.argmax(ratio)

ax_crit = sig_ax[i_crit]
hoop_crit = sig_hoop[i_crit]

# -----------------------------
# ELIPSE REAL VM
# -----------------------------
sig_ax_vals = np.linspace(-yield_ksi, yield_ksi, 1000)

sig_hoop_pos = []
sig_hoop_neg = []

for s_ax in sig_ax_vals:
    disc = 4*yield_ksi**2 - 3*s_ax**2

    if disc >= 0:
        root = np.sqrt(disc)
        sig_hoop_pos.append((s_ax + root)/2)
        sig_hoop_neg.append((s_ax - root)/2)
    else:
        sig_hoop_pos.append(np.nan)
        sig_hoop_neg.append(np.nan)

# -----------------------------
# PLOT
# -----------------------------
fig, ax = plt.subplots(figsize=(7,7))

# elipse correcta
ax.plot(sig_ax_vals, sig_hoop_pos, color="blue")
ax.plot(sig_ax_vals, sig_hoop_neg, color="blue")

# trayectoria
ax.plot(sig_ax, sig_hoop, color="orange", linewidth=2)

# punto crítico
ax.scatter(ax_crit, hoop_crit, color="red", s=120)

# formato
lim = yield_ksi * 1.1

ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

ax.set_aspect("equal")

ax.axhline(0, color="black")
ax.axvline(0, color="black")

ax.set_xlabel("σ axial (ksi)")
ax.set_ylabel("σ circunferencial (ksi)")

ax.grid()

st.pyplot(fig)

# -----------------------------
# RESULTADO
# -----------------------------
st.metric("Ratio máximo", round(float(np.max(ratio)), 3))
``
