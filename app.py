import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Diseño OCTG - Von Misses")

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
# GEOMETRIA
# =========================================
def area_metal(OD, ID):
    return np.pi * (OD**2 - ID**2) / 4

# =========================================
# TUBOS
# =========================================
tubos = {
    '2 7/8" #6.5': (2.876, 2.440, 6.5),
    '2 7/8" #4.05': (2.876, 2.6, 4),
    '3 1/2" #9.2': (3.500, 2.992, 9.2),
    '3 1/2" #7.7': (3.500, 3.068, 7.7),
    '5 1/2" #15.5': (5.500, 4.960, 15.5),
    '7" #23': (7.000, 6.360, 23.0),
    '9 5/8" #36': (9.620, 8.760, 36.0),
}

# =========================================
# INPUTS
# =========================================
st.sidebar.header("Inputs")

tubo = st.sidebar.selectbox(
    "Tube",
    list(tubos.keys())
)
OD, ID, peso = tubos[tubo]
peso = peso * 1.02
liner = st.sidebar.selectbox(
    "liner interno",
    ["Sin liner", "Con liner"]
)
if liner == "Con liner":

    t_liner = 4 / 25.4      # in
    t_cemento = 1 / 25.4    # in

    rho_ppa = 0.95         # g/cm3
    rho_cem = 1.80          # g/cm3

    ID_original = ID

    A_ppa = np.pi/4 * (
        ID_original**2
        - (ID_original - 2*t_liner)**2
    )

    A_cem = np.pi/4 * (
        (ID_original - 2*t_liner)**2
        - (ID_original - 2*t_liner - 2*t_cemento)**2
    )

    peso_ppa = A_ppa * rho_ppa * 0.491
    peso_cem = A_cem * rho_cem * 0.491

    peso += peso_ppa + peso_cem
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

condicion = st.sidebar.selectbox(
    "Condición",
    ["Libre","Anclado","Packer"]
)

P_iny = st.sidebar.number_input(
    "Injection Pressure [psi]",
    value=2000.0
)

Pext_surface = st.sidebar.number_input(
    "Pressure Casing [psi]",
    value=0.0
)

rho_int = st.sidebar.number_input(
    "ρ interno [kg/m³]",
    value=1090.0
)

rho_ext = st.sidebar.number_input(
    "ρ Ext. [kg/m³]",
    value=1000.0
)

fill_int = (
    st.sidebar.slider(
        "Int. fluid filled [%]",
        0,
        100,
        100
    ) / 100
)

fill_ext = (
    st.sidebar.slider(
        "Ext. fluid filled [%]",
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
    "Axial Ext Load [lbf]",
    value=0.0
)

depth_m = st.sidebar.number_input(
    "Depth [m]",
    value=3000.0
)

depth_ft = m_to_ft(depth_m)

rho_int = kgm3_to_lbft3(rho_int)
rho_ext = kgm3_to_lbft3(rho_ext)

# =========================================
# PERFIL
# =========================================
sig_ax = []
sig_hoop = []
vm_list = []
z_list = []

for i in range(200):

    z = depth_ft * i / 199

    z_int = z * fill_int
    z_ext = z * fill_ext

    # ==========================
    # PRESIONES
    # ==========================
    Pi = (
        P_iny
        + rho_int * z_int / 144
    )

    Po = (
        Pext_surface
        + rho_ext * z_ext / 144
    )

    # ==========================
    # GEOMETRIA
    # ==========================
    A = area_metal(OD, ID)

    ri = ID / 2
    ro = OD / 2

    # ==========================
    # AXIAL MECANICO
    # ==========================
    A_ext_ft2 = (np.pi * OD**2 / 4) / 144

    F_weight = peso * z

    F_buoy = (
        rho_ext *
        fill_ext *
        z *
        A_ext_ft2
    )

    F_total = (
        F_weight
        - F_buoy
        + F_ext
    )

    sigma_ax = F_total / A

    # ==========================
    # AXIAL POR PRESION
    # ==========================
    if condicion == "Libre":

        sigma_pressure = 0

    else:

        sigma_pressure = (
            Pi * ri**2
            - Po * ro**2
        ) / (
            ro**2 - ri**2
        )

    sa = sigma_ax + sigma_pressure

    # ==========================
    # HOOP
    # ==========================
    t = (OD - ID) / 2

    sh = (
        (Pi - Po)
        * OD
        / (2*t)
    )

    # ==========================
    # RADIAL
    # ==========================
    sr = -Po

    # ==========================
    # TORSION
    # ==========================
    T = Torque * 12

    J = (
        np.pi / 2
        * (ro**4 - ri**4)
    )

    tau = 0

    if J > 0:
        tau = T * ro / J

    # ==========================
    # VON MISES
    # ==========================
    vm = np.sqrt(
     sa**2
     + sh**2
     - sa*sh
     + 3*tau**2
)
    sig_ax.append(sa / 1000)
    sig_hoop.append(sh / 1000)
    vm_list.append(vm / 1000)
    z_list.append(z)

sig_ax = np.array(sig_ax)
sig_hoop = np.array(sig_hoop)
vm_list = np.array(vm_list)

# =========================================
# CRITICO
# =========================================
i_crit = np.argmax(vm_list)

sx = sig_ax[i_crit]
sy = sig_hoop[i_crit]
vm_crit = vm_list[i_crit]

z_crit = ft_to_m(z_list[i_crit])

# =========================================
# ELIPSE VM
# =========================================
s = np.linspace(
    -SMYS,
    SMYS,
    2000
)

x_vm = []
y1 = []
y2 = []

for val in s:

    disc = (
        4 * SMYS**2
        - 3 * val**2
    )

    if disc >= 0:

        root = np.sqrt(disc)

        x_vm.append(val)
        y1.append((val + root)/2)
        y2.append((val - root)/2)

# =========================================
# GRAFICO
# =========================================
fig, ax = plt.subplots(
    figsize=(8,8)
)

ax.fill(
    x_vm,
    y1,
    alpha=0.20
)

ax.plot(x_vm, y1, lw=2)
ax.plot(x_vm, y2, lw=2)

util_profile = vm_list / SMYS * 100

sc = ax.scatter(
    sig_ax,
    sig_hoop,
    c=util_profile,
    cmap="turbo",
    s=25
)

plt.colorbar(
    sc,
    ax=ax,
    label="Utilización [%]"
)

ax.scatter(
    sx,
    sy,
    color="red",
    s=250,
    edgecolors="black",
    linewidths=2,
    zorder=10
)

ax.annotate(
    f"VM={vm_crit:.1f} ksi",
    (sx, sy),
    xytext=(15,15),
    textcoords="offset points",
    bbox=dict(
        boxstyle="round",
        fc="white"
    )
)

ax.axhline(0, color="black", lw=2)
ax.axvline(0, color="black", lw=2)

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
# Conclusions
# =========================================
st.subheader("Conclusions")

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
    "Prof crítica [m]",
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
