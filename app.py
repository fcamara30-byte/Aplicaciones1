import streamlit as st
import matplotlib.pyplot as plt
from modelo import *

st.title("Modelo Von Mises - Tubing")

# ---------------------------
# BASE API SIMPLE
# ---------------------------
api_data = {
    "2 7/8": {"OD": 2.875, "t": 0.217},
    "3 1/2": {"OD": 3.5, "t": 0.254},
    "4 1/2": {"OD": 4.5, "t": 0.337},
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

size = st.sidebar.selectbox("Tubing API", list(api_data.keys()))
grade_name = st.sidebar.selectbox("Grado", list(grades.keys()))

yield_ksi = grades[grade_name]

OD = api_data[size]["OD"]
t = api_data[size]["t"]
ID = OD - 2*t

st.sidebar.write(f"OD: {OD} in")
st.sidebar.write(f"ID: {round(ID,3)} in")

rho_int = st.sidebar.number_input("Densidad interna (kg/m3)", value=1050)
rho_ext = st.sidebar.number_input("Densidad externa (kg/m3)", value=1200)

fill_int = st.sidebar.slider("Fill interno", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Fill externo", 0.0, 1.0, 1.0)

Pint_surface = st.sidebar.number_input("P interna (psi)", value=1500.0)
Pext_surface = st.sidebar.number_input("P externa (psi)", value=0.0)

Torque = st.sidebar.number_input("Torque (lb-ft)", value=0.0)

prof_max = st.sidebar.number_input("Profundidad (m)", value=2000)

# ---------------------------
# CALCULO AUTOMATICO
# ---------------------------
zs = []
ratios = []

peor_ratio = 0
peor_z = 0

for i in range(100):
    z = prof_max * i / 100

    Pint = presion(z, Pint_surface, rho_int, fill_int)
    Pext = presion(z, Pext_surface, rho_ext, fill_ext)

    DeltaP = Pint - Pext

    sig_hoop = tension_circunferencial(DeltaP, OD, t)
    sig_ax = tension_axial(z, OD, ID, rho_int, rho_ext)
    tau = tension_torsion(Torque, OD, ID)

    vm = von_mises(sig_ax, sig_hoop, tau)
    ratio = vm / yield_ksi

    zs.append(z)
    ratios.append(ratio)

    if ratio > peor_ratio:
        peor_ratio = ratio
        peor_z = z

# ---------------------------
# RESULTADOS
# ---------------------------
st.subheader("Resultados")

st.write(f"Profundidad crítica: {round(peor_z,2)} m")
st.write(f"Ratio VM: {round(peor_ratio,3)}")

if peor_ratio > 1:
    st.error("FALLA")
elif peor_ratio > 0.9:
    st.warning("CERCA DEL LÍMITE")
else:
    st.success("SEGURO")

# ---------------------------
# ELIPSE VON MISES
# ---------------------------
fig, ax = plt.subplots()

sigma_ax_vals = []
sigma_hoop_vals = []

for i in range(-100, 100):
    s_ax = yield_ksi * i / 100

    disc = yield_ksi**2 - (s_ax**2 - s_ax*0)

    disc = 4*yield_ksi**2 - 3*s_ax**2

    if disc >= 0:
        root = disc**0.5

        s_hoop1 = (s_ax + root)/2
        s_hoop2 = (s_ax - root)/2

        sigma_ax_vals.append(s_ax)
        sigma_hoop_vals.append(s_hoop1)

        sigma_ax_vals.append(s_ax)
        sigma_hoop_vals.append(s_hoop2)

ax.scatter(sigma_ax_vals, sigma_hoop_vals, s=5, label="Envolvente VM")

# punto
Pint = presion(peor_z, Pint_surface, rho_int, fill_int)
Pext = presion(peor_z, Pext_surface, rho_ext, fill_ext)

DeltaP = Pint - Pext

sig_hoop = tension_circunferencial(DeltaP, OD, t)
sig_ax = tension_axial(peor_z, OD, ID, rho_int, rho_ext)

ax.scatter(sig_ax, sig_hoop, color="red", s=120, label="Punto crítico")

# formato correcto
lim = yield_ksi * 1.2

ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

ax.set_aspect('equal')
ax.axhline(0, color='black')
ax.axvline(0, color='black')

ax.set_xlabel("σ axial (ksi)")
ax.set_ylabel("σ circunferencial (ksi)")

ax.legend()
ax.grid()

st.pyplot(fig)



