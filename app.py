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
# FUNCIONES
# =========================================
def area_metal(OD, ID):
    return np.pi * (OD**2 - ID**2) / 4

def hoop_stress(Pi, Po, OD, ID):

    t = (OD - ID) / 2

    return (Pi - Po) * OD / (2 * t)

def radial_stress(Pi):
    return -Pi

def torsion(Torque_lbft, OD, ID):

    T = Torque_lbft * 12

    ro = OD / 2
    ri = ID / 2

    J = np.pi / 2 * (ro**4 - ri**4)

    if J <= 0:
        return 0

    return T * ro / J

def axial_stress(
    OD,
    ID,
    peso_lbft,
    z_ft,
    rho_ext_lbft3,
    fill_ext,
    F_ext=0
):

    A = area_metal(OD, ID)

    A_ext_ft2 = (np.pi * OD**2 / 4) / 144

    F_weight = peso_lbft * z_ft

    F_buoy = (
        rho_ext_lbft3 *
        fill_ext *
        z_ft *
        A_ext_ft2
    )

    F_total = (
        F_weight
        - F_buoy
        + F_ext
    )

    return F_total / A

def von_mises(sa, sh, sr, tau):

    return np.sqrt(
        0.5 * (
            (sa - sh)**2 +
            (sh - sr)**2 +
            (sr - sa)**2
        )
        + 3 * tau**2
    )

# =========================================
# TUBOS
# =========================================
tubos = {
    '7" #23': (7.000, 6.622, 23.0),
    '5 1/2" #15.5': (5.500, 4.778, 15.5),
    '3 1/2" #9.2': (3.500, 2.992, 9.2),
    '2 7/8" #6.5': (2.875, 2.441, 6.5),
}

# =========================================
# INPUTS
# =========================================
st.sidebar.header("Inputs")

tubo = st.sidebar.selectbox(
    "Tubing",
    list(tubos.keys())
)

OD, ID, peso = tubos[tubo]

perdida_pct = st.sidebar.slider(
    "Pérdida de espesor [%]",
    0,
    100,
    0
)

t_original = (OD - ID) / 2
t_actual = t_original * (1 - perdida_pct / 100)

ID = OD - 2 * t_actual

grado = st.sidebar.selectbox(
    "Grado",
    ["J55","N80","P110","Q125"]
)

SMYS = {
    "J55":55,
    "N80":80,
    "P110":110,
    "Q125":125
}[grado]

P_iny = st.sidebar.number_input(
    "Presión de inyección [psi]",
    value=2000.0
)

rho_int = st.sidebar.number_input(
    "ρ interno [kg/m³]",
    value=1090.0
)

rho_ext = st.sidebar.number_input(
    "ρ externo [kg/m³]",
    value=1000.0
)

fill_int = (
    st.sidebar.slider(
        "Nivel interno [%]",
        0,
        100,
        100
    ) / 100
)

fill_ext = (
    st.sidebar.slider(
        "Nivel externo [%]",
        0,
        100,
        100
    ) / 100
)

Torque = st.sidebar.number_input(
    "Torque [lb-ft]",
    value=0.0
)

F_ext = st.sidebar.number_input(
    "Fuerza axial externa [lbf]",
    value=0.0
)

depth_m = st.sidebar.number_input(
    "Profundidad [m]",
    value=3000.0
)

depth_ft = m_to_ft(depth_m)

rho_int = kgm3_to_lbft3(rho_int)
rho_ext = kgm3_to_lbft3(rho_ext)

# =========================================
# CALCULO PERFIL
# =========================================
sig_ax = []
sig_hoop = []
vm_list = []
z_list = []

for i in range(200):

    z = depth_ft * i / 199

    z_int = z * fill_int
    z_ext = z * fill_ext

    Pi = (
        P_iny +
        rho_int * z_int / 144
    )

    Po = (
        rho_ext * z_ext / 144
    )

    sa = axial_stress(
        OD,
        ID,
        peso,
        z,
        rho_ext,
        fill_ext,
        F_ext
    )

    sh = hoop_stress(
        Pi,
        Po,
        OD,
        ID
    )

    sr = radial_stress(Pi)

    tau = torsion(
        Torque,
        OD,
        ID
    )

    vm = von_mises(
        sa,
        sh,
        sr,
        tau
    )

    sig_ax.append(sa / 1000)
    sig_hoop.append(sh / 1000)
    vm_list.append(vm / 1000)
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
vm_crit = vm_list[i_crit]

z_crit = ft_to_m(z_list[i_crit])

# =========================================
# ENVOLVENTE VON MISES
# =========================================
s = np.linspace(-SMYS, SMYS, 2000)

x_vm = []
y1 = []
y2 = []

for val in s:

    disc = 4 * SMYS**2 - 3 * val**2

    if disc >= 0:

        root = np.sqrt(disc)

        x_vm.append(val)
        y1.append((val + root)/2)
        y2.append((val - root)/2)

# =========================================
# GRAFICO
# =========================================
fig, ax = plt.subplots(figsize=(7,7))

ax.plot(x_vm, y1, 'b')
ax.plot(x_vm, y2, 'b')

ax.plot(
    sig_ax,
    sig_hoop,
    color="orange",
    lw=2
)

ax.scatter(
    sx,
    sy,
    color="red",
    s=120
)

ax.axhline(0,color='black')
ax.axvline(0,color='black')

ax.axhline(SMYS,color='red',ls='--')
ax.axhline(-SMYS,color='red',ls='--')
ax.axvline(SMYS,color='red',ls='--')
ax.axvline(-SMYS,color='red',ls='--')

lim = SMYS * 1.10

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

c1.metric(
    "σ axial [ksi]",
    round(sx,2)
)

c1.metric(
    "σ hoop [ksi]",
    round(sy,2)
)

c2.metric(
    "Von Mises [ksi]",
    round(vm_crit,2)
)

c2.metric(
    "Prof. crítica [m]",
    round(z_crit,0)
)

util = vm_crit / SMYS * 100

c3.metric(
    "Utilización [%]",
    round(util,1)
)

c3.metric(
    "Estado",
    "PASS" if vm_crit < SMYS else "FAIL"
)
