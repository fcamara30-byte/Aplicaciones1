import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from modelo import *

st.title("Modelo Von Mises - Tubing")

# ---------------------------
# BASE API REALISTA (simplificada)
# ---------------------------
api_db = {
    "2 7/8": {
        6.4: {"OD": 2.875, "t": 0.217},
        8.6: {"OD": 2.875, "t": 0.276},
    },
    "3 1/2": {
        9.3: {"OD": 3.5, "t": 0.254},
        12.95: {"OD": 3.5, "t": 0.318},
    },
    "4 1/2": {
        11.6: {"OD": 4.5, "t": 0.237},
        15.1: {"OD": 4.5, "t": 0.337},
    }
}

grades = {
    "J55": 55,
    "N80": 80,
    "P110": 110
}

# ---------------------------
# INPUTS
# ---------------------------
st.sidebar.header("Inputs")

size = st.sidebar.selectbox("OD", list(api_db.keys()))
weights = list(api_db[size].keys())

weight = st.sidebar.selectbox("lb/ft", weights)

grade_name = st.sidebar.selectbox("Grado", list(grades.keys()))
yield_ksi = grades[grade_name]

OD = api_db[size][weight]["OD"]
t = api_db[size][weight]["t"]
ID = OD - 2*t

st.sidebar.write(f"OD: {OD}")
st.sidebar.write(f"ID: {round(ID,3)}")

rho_int = st.sidebar.number_input("ρ interno", value=1050)
rho_ext = st.sidebar.number_input("ρ externo", value=1200)

fill_int = st.sidebar.slider("Fill int", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Fill ext", 0.0, 1.0, 1.0)

Pint_surface = st.sidebar.number_input("Pint", value=1500.0)
Pext_surface = st.sidebar.number_input("Pext", value=0.0)

Torque = st.sidebar.number_input("Torque (lb-ft)", value=0.0)
prof_max = st.sidebar.number_input("Prof (m)", value=2000)

# ---------------------------
# CALCULO
# ---------------------------
zs = []
sig_ax_list = []
sig_hoop_list = []

peor_ratio = 0
peor_i = 0

for i in range(100):
    z = prof_max * i / 100

    Pint = presion(z, Pint_surface, rho_int, fill_int)
    Pext = presion(z, Pext_surface, rho_ext, fill_ext)

    dP = Pint - Pext

    sig_hoop = tension_circunferencial(dP, OD, t)
    sig_ax = tension_axial(z, OD, ID, rho_int, rho_ext)
    tau = tension_torsion(Torque, OD, ID)

    vm = von_mises(sig_ax, sig_hoop, tau)
    ratio = vm / yield_ksi

    sig_ax_list.append(sig_ax)
    sig_hoop_list.append(sig_hoop)

    if ratio > peor_ratio:
        peor_ratio = ratio
        peor_i = i

# punto crítico
sig_ax_crit = sig_ax_list[peor_i]
sig_hoop_crit = sig_hoop_list[peor_i]

# ---------------------------
# ELIPSE CORRECTA
# ---------------------------
fig, ax = plt.subplots()

theta = np.linspace(0, 2*np.pi, 400)

R = yield_ksi

# forma Von Mises (aprox proyectada)
x = R * np.cos(theta)
y = R * np.sin(theta)

ax.plot(x, y, label="Envolvente VM")

# trayectoria
ax.plot(sig_ax_list, sig_hoop_list, color="orange", label="Trayectoria")

# punto crítico
ax.scatter(sig_ax_crit, sig_hoop_crit, color="red", s=120, label="Crítico")

# formato
lim = yield_ksi * 1.2

ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

ax.set_aspect("equal")

ax.axhline(0, color="black")
ax.axvline(0, color="black")

ax.set_xlabel("σ axial (ksi)")
ax.set_ylabel("σ circunferencial (ksi)")

ax.legend(loc="upper left")

ax.grid()

st.pyplot(fig)


