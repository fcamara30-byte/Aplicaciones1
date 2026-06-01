import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *

st.set_page_config(layout="wide")
st.title("Modelo Von Mises")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Configuración")

modo = st.sidebar.radio("Modo", ["API", "Custom"])

api = {
    "7": {
        23.0: (7.0, 0.317),
        26.0: (7.0, 0.362),
        29.0: (7.0, 0.408)
    }
}

# -----------------------------
# GEOMETRIA
# -----------------------------
st.sidebar.subheader("Tubing")

size = st.sidebar.selectbox("OD [in]", api.keys())
weight = st.sidebar.selectbox("Peso [lb/ft]", api[size].keys())

OD, t = api[size][weight]
ID = OD - 2*t

st.sidebar.markdown(f"""
### Geometría
- OD: {OD} in  
- ID: {round(ID,3)} in  
- t: {round(t,3)} in  
""")

# -----------------------------
# MATERIAL
# -----------------------------
yield_ksi = st.sidebar.selectbox("Yield [ksi]", [55, 80, 110])

# -----------------------------
# FLUIDOS
# -----------------------------
rho_int = st.sidebar.number_input("Densidad interna [kg/m³]", value=1050)
rho_ext = st.sidebar.number_input("Densidad externa [kg/m³]", value=1200)

fill_int = st.sidebar.slider("Fill interno [-]", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Fill externo [-]", 0.0, 1.0, 1.0)

# -----------------------------
# PRESIONES
# -----------------------------
Pint = st.sidebar.number_input("P interna [psi]", value=1500.0)
Pext = st.sidebar.number_input("P externa [psi]", value=0.0)

# -----------------------------
# MECÁNICO
# -----------------------------
Torque = st.sidebar.number_input("Torque [lb·ft]", value=0.0)

F_ext = st.sidebar.number_input(
    "Fuerza axial externa [lbf]\n(+ tracción / - compresión)",
    value=0.0
)

prof_max = st.sidebar.number_input("Profundidad [m]", value=2000.0)

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

    s_ax = tension_axial(z, OD, ID, rho_int, rho_ext, F_ext)

    # ✅ efecto presión axial
    Area_int = np.pi * ID**2 / 4
    Area_sec = np.pi * (OD**2 - ID**2) / 4

    s_ax += (Pint_z - Pext_z) * (Area_int / Area_sec) / 1000

    sig_ax.append(s_ax)
    sig_hoop.append(s_hoop)

sig_ax = np.array(sig_ax)
sig_hoop = np.array(sig_hoop)

# -----------------------------
# VM
# -----------------------------
tau = torsion(Torque, OD, ID)

vm = np.sqrt(sig_ax**2 + sig_hoop**2 - sig_ax*sig_hoop + 3*tau**2)

ratio = vm / yield_ksi

i_crit = np.argmax(ratio)

ax_c = sig_ax[i_crit]
hoop_c = sig_hoop[i_crit]

# -----------------------------
# ELIPSE (CORRECTA Y CERRADA)
# -----------------------------
sigma_ax = np.linspace(-yield_ksi, yield_ksi, 2000)

top = []
bot = []

for s in sigma_ax:
    disc = 4*yield_ksi**2 - 3*s**2

    if disc >= 0:
        root = np.sqrt(disc)
        top.append((s + root)/2)
        bot.append((s - root)/2)
    else:
        top.append(np.nan)
        bot.append(np.nan)

x_ellipse = np.concatenate([sigma_ax, sigma_ax[::-1]])
y_ellipse = np.concatenate([top, bot[::-1]])

# -----------------------------
# PLOT
# -----------------------------
fig, ax = plt.subplots(figsize=(7,7))

ax.plot(x_ellipse, y_ellipse, color="blue", linewidth=2)

ax.plot(sig_ax, sig_hoop, color="orange", linewidth=2)

ax.scatter(ax_c, hoop_c, color="red", s=120)

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
ax.set_ylabel("σ circunferencial [ksi]")

ax.grid()

st.pyplot(fig)

st.metric("VM/Yield", round(float(max(ratio)), 3))
