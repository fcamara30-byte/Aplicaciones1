import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Diseño OCTG - Von Mises")

# =========================================
# CONVERSIONES
# =========================================
def kgm3_to_lbft3(rho):
    return rho * 0.062428

def m_to_ft(z):
    return z * 3.28084

def ft_to_m(z):
    return z / 3.28084

# =========================================
# BASE TUBOS
# =========================================
tubos = {
    "7\" #23": (7.0, 6.622, 23),
    "5 1/2\" #15.5": (5.5, 4.778, 15.5),
    "3 1/2\" #9.2": (3.5, 2.992, 9.2),
    "2 7/8 \" #6.5": (2.875, 2.441, 6.5),
}

# =========================================
# INPUTS
# =========================================
st.sidebar.title("Inputs")

tubo = st.sidebar.selectbox("Tubing", list(tubos.keys()))
OD, ID, peso = tubos[tubo]

# CORROSION
perdida_pct = st.sidebar.slider("Pérdida de espesor [%]", 0, 100, 0)
perdida = perdida_pct / 100

t_original = (OD - ID) / 2
t_actual = t_original * (1 - perdida)
ID = OD - 2 * t_actual

if t_actual <= 0:
    st.sidebar.error("Espesor nulo")

# MATERIAL
grado = st.sidebar.selectbox("Grado", ["J55","N80","P110","Q125"])
SMYS = {"J55":55,"N80":80,"P110":110,"Q125":125}[grado]

# PRESION
P_iny = st.sidebar.number_input("Presión de inyección [psi]", value=2000.0)

# DENSIDADES
rho_int = kgm3_to_lbft3(st.sidebar.number_input("ρ interno [kg/m³]", value=1090.0))
rho_ext = kgm3_to_lbft3(st.sidebar.number_input("ρ externo [kg/m³]", value=1000.0))

# NIVELES
fill_int = st.sidebar.slider("Nivel interno [%]", 0, 100, 100) / 100
fill_ext = st.sidebar.slider("Nivel externo [%]", 0, 100, 100) / 100

# TORQUE
Torque = st.sidebar.number_input("Torque [lb-ft]", value=0.0)

# PROFUNDIDAD
depth_m = st.sidebar.number_input("Profundidad [m]", value=3000.0)
depth_ft = m_to_ft(depth_m)

# =========================================
# PERFIL
# =========================================
sig_ax, sig_hoop, vm_list, z_list = [], [], [], []

for i in range(200):

    z = depth_ft * i / 199

    # ========================
    # PRESIONES
    # ========================
    z_int = z * fill_int
    z_ext = z * fill_ext

    P_int = rho_int * z_int / 144 / 1000  # ksi
    P_ext = rho_ext * z_ext / 144 / 1000  # ksi

    Pi = P_int + (P_iny / 1000)

    # ========================
    # GEOMETRIA
    # ========================
    t = (OD - ID) / 2
    A = np.pi/4 * (OD**2 - ID**2)
    A_ext = np.pi/4 * (OD**2)

    # ========================
    # HOOP (ΔP)
    # ========================
    hoop = (Pi - P_ext) * OD / (2 * t)

    # ========================
    # AXIAL (CON FLOTACION REAL)
    # ========================
    F_weight = peso * z                   # peso tubo
    F_buoy = rho_ext * z_ext * A_ext      # empuje fluido externo

    F_eff = F_weight - F_buoy             # carga efectiva
    sigma_ax = F_eff / A / 1000          # ksi

    # ========================
    # RADIAL
    # ========================
    sigma_r = -P_ext

    # ========================
    # TORSION
    # ========================
    T = Torque * 12
    ro = OD / 2
    ri = ID / 2
    J = np.pi/2 * (ro**4 - ri**4)
    tau = T * ro / J if J > 0 else 0

    # ========================
    # VON MISES
    # ========================
    vm = np.sqrt(
        0.5 * (
            (sigma_ax - hoop)**2 +
            (hoop - sigma_r)**2 +
            (sigma_r - sigma_ax)**2
        )
        + 3 * tau**2
    )

    sig_ax.append(sigma_ax)
    sig_hoop.append(hoop)
    vm_list.append(vm)
    z_list.append(z)

sig_ax = np.array(sig_ax)
sig_hoop = np.array(sig_hoop)
vm_list = np.array(vm_list)

# =========================================
# PUNTO CRITICO
# =========================================
i_crit = np.argmax(vm_list)

sx = sig_ax[i_crit]
sy = sig_hoop[i_crit]
z_crit = ft_to_m(z_list[i_crit])

# =========================================
# ELIPSE
# =========================================
Sy = SMYS
s = np.linspace(-Sy, Sy, 2000)

x_vm, y1, y2 = [], [], []

for val in s:
    disc = 4*Sy**2 - 3*val**2
    if disc >= 0:
        root = np.sqrt(disc)
        x_vm.append(val)
        y1.append((val + root)/2)
        y2.append((val - root)/2)

# =========================================
# GRAFICO
# =========================================
fig, ax = plt.subplots(figsize=(7,7))

ax.plot(x_vm, y1, 'b', lw=2)
ax.plot(x_vm, y2, 'b', lw=2)

ax.plot(sig_ax, sig_hoop, color="orange", lw=2)
ax.scatter(sx, sy, color="red", s=150)

ax.axhline(0, color="black")
ax.axvline(0, color="black")

ax.axhline(SMYS, color="red", ls="--")
ax.axhline(-SMYS, color="red", ls="--")
ax.axvline(SMYS, color="red", ls="--")
ax.axvline(-SMYS, color="red", ls="--")

lim = SMYS * 1.1
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

ax.set_aspect("equal")
ax.grid(True)

ax.set_xlabel("σ axial [ksi]")
ax.set_ylabel("σ hoop [ksi]")

st.pyplot(fig)

# =========================================
# RESULTADOS
# =========================================
st.subheader("Resultados")

c1, c2, c3 = st.columns(3)

c1.metric("σ axial [ksi]", round(sx,2))
c1.metric("σ hoop [ksi]", round(sy,2))

