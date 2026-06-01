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

def ft_to_m(z):
    return z / 3.28084

def m_to_ft(z):
    return z * 3.28084


# =========================================
# BASE TUBOS
# =========================================
tubos = {
    "7 #23": (7.0, 6.622, 23)
}

# =========================================
# INPUTS
# =========================================
st.sidebar.title("Inputs")

tubo = st.sidebar.selectbox("Tubing", list(tubos.keys()))
OD, ID, peso = tubos[tubo]

grado = st.sidebar.selectbox("Grado", ["J55","N80","P110","Q125"])
SMYS = {"J55":55,"N80":80,"P110":110,"Q125":125}[grado]

modo = st.sidebar.selectbox("Condición axial", ["Libre","Anclado","Packer"])

P_iny = st.sidebar.number_input("Presión de inyección [psi]", value=0.0)
Pext_surface = st.sidebar.number_input("Presión externa superficial [psi]", value=0.0)

rho_int_si = st.sidebar.number_input("ρ interno [kg/m³]", 1000.0)
rho_ext_si = st.sidebar.number_input("ρ externo [kg/m³]", 1000.0)

rho_int = kgm3_to_lbft3(rho_int_si)
rho_ext = kgm3_to_lbft3(rho_ext_si)

fill_int = st.sidebar.slider("Nivel interno [-]", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Nivel externo [-]", 0.0, 1.0, 1.0)

depth_m = st.sidebar.number_input("Profundidad [m]", 3000.0)
depth_ft = m_to_ft(depth_m)

# =========================================
# PERFIL
# =========================================
sig_ax, sig_hoop, vm_list, z_list = [], [], [], []

tau = torsion(0, OD, ID)

for i in range(200):

    z = depth_ft * i / 200

    Pi = P_iny + (rho_int * z) / 144
    Po = Pext_surface + (rho_ext * z) / 144

    ax_val = axial_load(
        OD, ID, peso, z,
        rho_int, rho_ext,
        fill_int, fill_ext,
        0,
        Pi, Po,
        modo
    )

    hoop = hoop_stress(Pi, Po, OD, ID)
    vm = von_mises(ax_val, hoop, tau)

    sig_ax.append(ax_val/1000)
    sig_hoop.append(hoop/1000)
    vm_list.append(vm)
    z_list.append(z)

sig_ax = np.array(sig_ax)
sig_hoop = np.array(sig_hoop)
vm_list = np.array(vm_list)

# =========================================
# PUNTO CRITICO
# =========================================
i_crit = np.argmax(vm_list)

x_crit = sig_ax[i_crit]
y_crit = sig_hoop[i_crit]
z_crit = ft_to_m(z_list[i_crit])

# =========================================
# ELIPSE
# =========================================
sy = SMYS

x_vm = []
y_vm = []

for s in np.linspace(-sy, sy, 2000):
    disc = 4*sy**2 - 3*s**2
    if disc >= 0:
        root = np.sqrt(disc)
        x_vm.append(s)
        y_vm.append((s + root)/2)

for s in np.linspace(sy, -sy, 2000):
    disc = 4*sy**2 - 3*s**2
    if disc >= 0:
        root = np.sqrt(disc)
        x_vm.append(s)
        y_vm.append((s - root)/2)

# =========================================
# PLOT
# =========================================
fig, ax = plt.subplots(figsize=(7,7))

ax.plot(x_vm, y_vm, color="blue", lw=2)
ax.plot(sig_ax, sig_hoop, color="orange", lw=2)

ax.scatter(x_crit, y_crit, color="red", s=150)

ax.axhline(0, color="black", lw=2)
ax.axvline(0, color="black", lw=2)

lim = SMYS * 1.1
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

ticks = np.arange(-SMYS, SMYS+1, 20)
ax.set_xticks(ticks)
ax.set_yticks(ticks)

ax.grid(True)
ax.set_aspect("equal")

ax.set_xlabel("σ axial [ksi]")
ax.set_ylabel("σ hoop [ksi]")

st.pyplot(fig)

# =========================================
# RESULTADOS
# =========================================
st.subheader("Resultados")

c1, c2, c3 = st.columns(3)

c1.metric("σ axial [ksi]", round(x_crit,2))
c1.metric("σ hoop [ksi]", round(y_crit,2))

c2.metric("Von Mises [ksi]", round(vm_list[i_crit]/1000,2))
c2.metric("Prof crítica [m]", round(z_crit,0))

c3.metric("Utilización [%]", round(utilization(SMYS, vm_list[i_crit]),1))
c3.metric("Estado", design_check(vm_list[i_crit], SMYS))

# =========================================
# PRINT (ARREGLADO)
# =========================================
import base64
from io import BytesIO

buf = BytesIO()
fig.savefig(buf, format="png", bbox_inches="tight")
img_str = base64.b64encode(buf.getvalue()).decode("utf-8")

html_report = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: Arial; margin: 30px; }}
h1 {{ text-align: center; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }}
</style>
</head>
<body>

<h1>Reporte Tubing</h1>

<div class="grid">
<div>Tubing: {tubo}</div>
<div>Grado: {grado}</div>
<div>σ axial: {round(x_crit,2)} ksi</div>
<div>σ hoop: {round(y_crit,2)} ksi</div>
<div>VM: {round(vm_list[i_crit]/1000,2)} ksi</div>
<div>Prof crítica: {round(z_crit,0)} m</div>
</div>

<img src="data:image/png;base64,{img_str}"/>

</body>
</html>
"""

if st.button("🖨️ Imprimir reporte"):
    st.components.v1.html(
        f"""
        <script>
        var w = window.open("", "", "width=900,height=700");
        w.document.write(`{html_report}`);
        w.document.close();
        w.focus();
        setTimeout(() => w.print(), 500);
        </script>
        """,
        height=0,
    )

