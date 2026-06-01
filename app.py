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

modo = st.sidebar.radio("Modo", ["API", "Custom"])

# -----------------------------
# BASE API
# -----------------------------
api = {
    "2 7/8": {6.4: (2.875, 0.217), 8.6: (2.875, 0.276)},
    "3 1/2": {9.3: (3.5, 0.254), 12.95: (3.5, 0.318)},
    "4 1/2": {11.6: (4.5, 0.237), 15.1: (4.5, 0.337)},
    "5 1/2": {17.0: (5.5, 0.304), 20.0: (5.5, 0.361)},
    "7": {
        23.0: (7.0, 0.317),
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

# -----------------------------
# GEOMETRIA
# -----------------------------
st.sidebar.subheader("Tubing")

if modo == "API":
    size = st.sidebar.selectbox("OD", api.keys())
    weight = st.sidebar.selectbox("lb/ft", api[size].keys())

    OD, t = api[size][weight]
    ID = OD - 2*t

else:
    OD = st.sidebar.number_input("OD (in)", value=3.5)
    weight = st.sidebar.number_input("lb/ft", value=10.0)

    t = weight / (10.69 * OD)
    ID = OD - 2*t

st.sidebar.markdown(f"""
### Geometría
- OD: {round(OD,3)} in  
- ID: {round(ID,3)} in  
- t: {round(t,3)} in  
""")

# -----------------------------
# MATERIAL
# -----------------------------
grades = {"J55": 55, "N80": 80, "P110": 110}
grado = st.sidebar.selectbox("Grado", grades.keys())
yield_ksi = grades[grado]

# -----------------------------
# FLUIDOS
# -----------------------------
rho_int = st.sidebar.number_input("ρ interno", value=1050)
rho_ext = st.sidebar.number_input("ρ externo", value=1200)

fill_int = st.sidebar.slider("Fill interno", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Fill externo", 0.0, 1.0, 1.0)

# -----------------------------
# PRESIONES
# -----------------------------
Pint = st.sidebar.number_input("P interna (psi)", value=1500.0)
Pext = st.sidebar.number_input("P externa (psi)", value=0.0)

# -----------------------------
# MECÁNICO
# -----------------------------
Torque = st.sidebar.number_input("Torque (lb-ft)", value=0.0)
prof_max = st.sidebar.number_input("Profundidad (m)", value=2000)

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
# ELIPSE CORRECTA (parametrica)
# -----------------------------
theta = np.linspace(0, 2*np.pi, 1000)

sigma_ax_ellipse = yield_ksi * (np.cos(theta) - 0.5*np.sin(theta))
sigma_hoop_ellipse = yield_ksi * (np.sin(theta) - 0.5*np.cos(theta))

# -----------------------------
# PLOT
# -----------------------------
fig, ax = plt.subplots(figsize=(7,7))

# elipse correcta
ax.plot(sigma_ax_ellipse, sigma_hoop_ellipse,
        color="blue", linewidth=2, label="Envolvente VM")

# trayectoria
ax.plot(sig_ax, sig_hoop, color="orange", linewidth=2, label="Trayectoria")

# punto crítico
ax.scatter(ax_crit, hoop_crit, color="red", s=120, label="Crítico")

# -----------------------------
# LINEAS LIMITE (ROJAS)
# -----------------------------
lim = yield_ksi

ax.axvline(lim, color="red", linestyle="--", linewidth=1)
ax.axvline(-lim, color="red", linestyle="--", linewidth=1)
ax.axhline(lim, color="red", linestyle="--", linewidth=1)


