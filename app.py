import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *

st.set_page_config(layout="wide")
st.title("Diseño Tubing - Von Mises")

# =========================================
# CONVERSIONES
# =========================================
def kgm3_to_lbft3(rho):
    return rho * 0.062428

def lbft3_to_kgm3(rho):
    return rho / 0.062428

def m_to_ft(z):
    return z * 3.28084

def ft_to_m(z):
    return z / 3.28084


# =========================================
# BASE TUBOS
# =========================================
tubos = {
    "2 7/8 #6.4": (2.875, 2.441, 6.4),
    "2 7/8 #4.04": (2.875, 2.565, 4.04),
    "3 1/2 #9.2": (3.5, 2.992, 9.2),
    "3 1/2 #7.7": (3.5, 3.068, 7.7),
    "5 1/2 #15.5": (5.5, 4.95, 15.5),
    "5 1/2 #10": (5.5, 5.095, 10),
    "7 #23": (7.0, 6.622, 23),
    "9 5/8 #36": (9.625, 8.921, 36),
    "9 5/8 #43.5": (9.625, 8.681, 43.5)
}

# =========================================
# INPUTS
# =========================================
st.sidebar.title("Inputs")

tubo = st.sidebar.selectbox("Tubing", list(tubos.keys()))
OD, ID, peso = tubos[tubo]

grado = st.sidebar.selectbox("Grado", ["J55","N80","P110","Q125"])
SMYS = {"J55":55, "N80":80, "P110":110, "Q125":125}[grado]

modo = st.sidebar.selectbox("Condición axial", ["Libre","Anclado","Packer"])

# ✅ presión bien definida
P_iny = st.sidebar.number_input("Presión de inyección [psi]", 0.0)
Pext_surface = st.sidebar.number_input("Presión externa superficial [psi]", 0.0)

# fluidos
rho_int_si = st.sidebar.number_input("ρ interno [kg/m³]", 1050.0)
rho_ext_si = st.sidebar.number_input("ρ externo [kg/m³]", 0.0)

rho_int = kgm3_to_lbft3(rho_int_si)
rho_ext = kgm3_to_lbft3(rho_ext_si)

fill_int = st.sidebar.slider("Nivel interno [-]", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Nivel externo [-]", 0.0, 1.0, 0.0)

Torque = st.sidebar.number_input("Torque [lb-ft]", 0.0)
F_ext = st.sidebar.number_input("F axial externa [lbf]", 0.0)

depth_m = st.sidebar.number_input("Profundidad total [m]", 3000.0)
depth_ft = m_to_ft(depth_m)

# =========================================
# PERFIL
# =========================================
sig_ax = []
sig_hoop = []
vm_list = []
z_list = []

tau = torsion(Torque, OD, ID)

for i in range(200):

    z = depth_ft * i / 200

    # ✅ presión interna calculada
    Pi = P_iny + (rho_int * fill_int * z) / 144

    # ✅ presión externa calculada
    Po = Pext_surface + (rho_ext * fill_ext * z) / 144

    ax_val = axial_load(
        OD, ID, peso, z,
        rho_int, rho_ext,
        fill_int, fill_ext,
        F_ext,
        Pi, Po,
        modo
    )

    hoop_val = hoop_stress(Pi, Po, OD, ID)

    vm_val = von_mises(ax_val, hoop_val, tau)

    sig_ax.append(ax_val / 1000)
    sig_hoop.append(hoop_val / 1000)
    vm_list.append(vm_val)
    z_list.append(z)

sig_ax = np.array(sig_ax)
sig_hoop = np.array(sig_hoop)
vm_list = np.array(vm_list)
z_list = np.array(z_list)

# =========================================
# PUNTO CRÍTICO
# =========================================
i_crit = np.argmax(vm_list)

sigma_ax = sig_ax[i_crit]
sigma_hoop = sig_hoop[i_crit]
vm_crit = vm_list[i_crit]

z_crit_m = ft_to_m(z_list[i_crit])

# =========================================
# API BURST
# =========================================
t = (OD - ID)/2
burst = burst_api(SMYS, t, OD)
burst_util = (P_iny / burst) * 100

# =========================================
# UTILIZACIÓN
# =========================================
util_vm = utilization(SMYS, vm_crit)

# =========================================
# ELIPSE
# =========================================
sy = SMYS * 0.9

s = np.linspace(-sy, sy, 2000)

x_vm, y_vm = [], []

for val in s:
    disc = 4*sy**2 - 3*val**2
    if disc >= 0:
        root = np.sqrt(disc)
        x_vm.append(val)
        y_vm.append((val + root)/2)

for val in reversed(s):
    disc = 4*sy**2 - 3*val**2
    if disc >= 0:
        root = np.sqrt(disc)
        x_vm.append(val)
        y_vm.append((val - root)/2)

# =========================================
# PLOT
# =========================================
fig, ax = plt.subplots(figsize=(7,7))

ax.plot(x_vm, y_vm, color="blue", lw=2)
ax.plot(sig_ax, sig_hoop, color="orange", lw=2)

# punto crítico
ax.scatter(sigma_ax, sigma_hoop, color="red", s=160)

ax.axhline(0, color="black", lw=1.5)
ax.axvline(0, color="black", lw=1.5)

lim = sy * 1.05
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

ticks = np.arange(-sy, sy+1, 20)
ax.set_xticks(ticks)
ax.set_yticks(ticks)

ax.grid(True, color="gray", lw=0.5)
ax.set_aspect("equal")

ax.set_xlabel("σ axial [ksi]")
ax.set_ylabel("σ hoop [ksi]")

st.pyplot(fig)

# =========================================
# RESULTADOS
# =========================================
st.subheader("Resultados")

col1, col2, col3 = st.columns(3)

col1.metric("σ axial [ksi]", round(sigma_ax,2))
col1.metric("σ hoop [ksi]", round(sigma_hoop,2))

col2.metric("Von Mises [ksi]", round(vm_crit/1000,2))
col2.metric("Utilización [%]", round(util_vm,1))

col3.metric("Burst Util [%]", round(burst_util,1))
col3.metric("Prof. crítica [m]", round(z_crit_m,0))

st.markdown(f"### Estado: **{design_check(vm_crit, SMYS)}**")

# =========================================
# REPORTE + IMPRESIÓN
# =========================================
st.markdown("---")
st.header("Reporte")

st.write(f"Tubing: {tubo}")
st.write(f"Grado: {grado}")
st.write(f"Presión de inyección: {P_iny} psi")
st.write(f"ρ interno: {rho_int_si} kg/m³")
st.write(f"ρ externo: {rho_ext_si} kg/m³")

st.markdown("### Imprimir")

if st.button("🖨️ Imprimir Reporte"):
    st.markdown(
        """
        <script>
        window.print();
        </script>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
<style>
@media print {
    .stSidebar {display:none;}
    button {display:none;}
}
</style>
""", unsafe_allow_html=True)
