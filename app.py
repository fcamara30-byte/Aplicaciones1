import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *
import base64
from io import BytesIO

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
# INPUTS (SIN RESTRICCIONES)
# =========================================
st.sidebar.title("Inputs")

tubo = st.sidebar.selectbox("Tubing", list(tubos.keys()))
OD, ID, peso = tubos[tubo]

grado = st.sidebar.selectbox("Grado", ["J55","N80","P110","Q125"])
SMYS = {"J55":55,"N80":80,"P110":110,"Q125":125}[grado]

modo = st.sidebar.selectbox("Condición axial", ["Libre","Anclado","Packer"])

P_iny = st.sidebar.number_input("Presión de inyección [psi]", value=0.0)
Pext_surface = st.sidebar.number_input("Presión externa superficial [psi]", value=0.0)

rho_int_si = st.sidebar.number_input("ρ interno [kg/m³]", value=0.0)
rho_ext_si = st.sidebar.number_input("ρ externo [kg/m³]", value=0.0)

rho_int = kgm3_to_lbft3(rho_int_si)
rho_ext = kgm3_to_lbft3(rho_ext_si)

fill_int = st.sidebar.slider("Nivel interno [-]", 0.0, 1.0, 0.0)
fill_ext = st.sidebar.slider("Nivel externo [-]", 0.0, 1.0, 0.0)

depth_m = st.sidebar.number_input("Profundidad [m]", value=3000.0)
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
# ELIPSE VM CORRECTA
# =========================================
sy = SMYS

theta = np.linspace(0, 2*np.pi, 2000)

x_vm = sy * np.cos(theta)
y_vm = sy * np.sin(theta)

# =========================================
# PLOT WELL-CAT STYLE
# =========================================
fig, ax = plt.subplots(figsize=(7,7))

# elipse
ax.plot(x_vm, y_vm, color="blue", lw=2)

# trayectoria
ax.plot(sig_ax, sig_hoop, color="orange", lw=2)

# punto crítico
ax.scatter(x_crit, y_crit, color="red", s=150)

# ejes
ax.axhline(0, color="black", lw=2)
ax.axvline(0, color="black", lw=2)

# límites
lim = max(SMYS*1.1, abs(x_crit)*1.2, abs(y_crit)*1.2)
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

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
# PRINT FUNCIONANDO
# =========================================
buf = BytesIO()
fig.savefig(buf, format="png", bbox_inches="tight")
img_str = base64.b64encode(buf.getvalue()).decode("utf-8")

html_report = f"""
<html>
<body>
<h2>Reporte Tubing</h2>

<p>Tubing: {tubo}</p>
<p>Grado: {grado}</p>
<p>σ axial: {round(x_crit,2)} ksi</p>
<p>σ hoop: {round(y_crit,2)} ksi</p>
<p>VM: {round(vm_list[i_crit]/1000,2)} ksi</p>
<p>Prof crítica: {round(z_crit,0)} m</p>

<img src="data:image/png;base64,{img_str}">

</body>
</html>
"""

if st.button("🖨️ Imprimir"):
    st.components.v1.html(
        f"""
        <script>
        var w = window.open();
        w.document.write(`{html_report}`);
        w.document.close();
        setTimeout(function(){{w.print();}},500);
        </script>
        """,
        height=0
    )


