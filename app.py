import pandas as pd
from io import BytesIO
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
st.session_state.setdefault("run_id", 0)

st.markdown("""
<style>

/* TABLA COMPLETA */
[data-testid="stDataFrame"] table {
    table-layout: fixed !important;
    width: 100% !important;
}

/* COLUMNAS MÁS ANGOSTAS */
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] td {
    text-align: center !important;   /* ✅ centra el texto */
    font-size: 12px !important;
    padding: 3px !important;
    width: 60px !important;          /* ✅ clave: ancho fijo */
    max-width: 60px !important;
}

/* FILAS MÁS BAJAS */
[data-testid="stDataFrame"] tr {
    height: 24px !important;
}

/* HEADERS */
[data-testid="stDataFrame"] th {
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* Expander cerrado y abierto */
details {
    background-color: #d4f7d4 !important;  /* verde claro elegante */
    border-radius: 10px;
    padding: 8px;
}

/* Texto del título del expander */
summary {
    font-weight: bold !important;
    color: #1b5e20 !important;  /* verde más oscuro */
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Fondo general */
.stApp {
    background-color: #f4f6f8;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #e9edf2;
}

/* Cards / métricas */
[data-testid="stMetric"] {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 10px;
}

/* Expander */
details {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 10px;
}

/* Título */
h1 {
    color: #1f2933;
}

/* Texto general */
body {
    color: #2e3a46;
}
</style>
""", unsafe_allow_html=True)
def color_vm(val):
    util = val / SMYS   # ← relación vs resistencia (no %, no hace falta *100)

    if util <= 0.6:
        return "background-color: #2ecc71"   # verde
    elif util <= 0.8:
        return "background-color: #f1c40f"   # amarillo
    elif util <= 1.0:
        return "background-color: #e67e22"   # naranja
    else:
        return "background-color: #e74c3c"   # rojo




st.set_page_config(layout="wide")
st.title("OCTG - Von Misses Calculation")

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
def area_metal(OD, ID):
    return np.pi * (OD**2 - ID**2) / 4
def calc_vm(depth_m, Piny, OD, ID, peso, rho_int, rho_ext,
            fill_int, fill_ext, Pext_surface,
            Torque, F_ext, Condition):

    depth_ft = m_to_ft(depth_m)

    A = area_metal(OD, ID)
    ri = ID / 2
    ro = OD / 2
    t = (OD - ID) / 2

    A_ext_ft2 = (np.pi * OD**2 / 4) / 144

    Pi = Piny + rho_int * depth_ft * fill_int / 144
    Po = Pext_surface + rho_ext * depth_ft * fill_ext / 144

    F_weight = peso * depth_ft

    # ✅ CORREGIDO (igual que el perfil)
    F_buoy = rho_ext * depth_ft * fill_ext * A_ext_ft2

    sigma_ax = (F_weight - F_buoy + F_ext) / A

    # ✅ CORREGIDO (igual que el perfil)
    if Condition == "Free":
        sigma_pressure = 0
    else:
        sigma_pressure = (
            Pi * ri**2 - Po * ro**2
        ) / (ro**2 - ri**2)

    sa = sigma_ax + sigma_pressure

    sh = (Pi - Po) * OD / (2 * t)

    T = Torque * 12
    J = (np.pi / 2) * (ro**4 - ri**4)

    tau = T * ro / J if J > 0 else 0

    vm = np.sqrt(sa**2 + sh**2 - sa * sh + 3 * tau**2)

    return vm / 1000


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
    '1" #2.91' : (1.0 , 0 , 2.91),
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

reduccion = st.sidebar.slider(
    "Wallthickness Reduction [%]",
    0,
    50,
    0
) / 100


t = (OD - ID) / 2
t = t * (1 - reduccion)
ID = OD - 2 * t


peso = peso * 1.02
liner = st.sidebar.selectbox(
    "Liner?",
    ["No Liner", "With Liner"]
)
if liner == "With Liner":

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
YP = SMYS * 1000   # psi
burst_api = 0.875 * 2 * SMYS * t / OD
collapse_api = (
    2 * SMYS *
    (t / OD)
)

Condition = st.sidebar.selectbox(
    "Condición",
    ["Free","Anchored","Packer"]
)

P_iny = st.sidebar.number_input(
    "Injection Pressure [psi]",
    value=2000.0,
    step=200.0,
    format="%.0f"
)

Pext_surface = st.sidebar.number_input(
    "Pressure Casing [psi]",
    value=0.0,
    step=150.0,
)

rho_int = st.sidebar.number_input(
    "ρ int.[kg/m³]",
    value=1090.0,
    
    step=100.0,
    format="%.0f"

)

rho_ext = st.sidebar.number_input(
    "ρ Ext. [kg/m³]",
    value=1000.0,
    
    step=100.0,
    format="%.0f"

)

fill_int = (
    st.sidebar.slider(
        "Tubing filled (%)",
        0,
        100,
        100
    ) / 100
)

fill_ext = (
    st.sidebar.slider(
        "Intercolumn filled (%)",
        0,
        100,
        0
    ) / 100
)

Torque = st.sidebar.number_input(
    "Torque [lb-ft]",
    value=0.0,
    
    step=100.0,
    format="%.0f"

)

F_ext = st.sidebar.number_input(
    "Axial Ext Load [lbf]",
    value=0.0,
    
    step=100.0,
    format="%.0f"

)

depth_m = st.sidebar.number_input(
    "Depth [m]",
    value=3000.0,
    step=100.0,
    format="%.0f"
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
    if Condition == "Free":

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
    (
        (sa - sh)**2 +
        (sh - sr)**2 +
        (sr - sa)**2
    ) / 2
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

from matplotlib.colors import Normalize

# =========================================
# NORMALIZACIÓN INGENIERÍA
# =========================================
util_profile = vm_list / SMYS * 100

# cortes típicos OCTG
# <60% verde
# 60-80% amarillo
# 80-100% naranja
# >100% rojo

bounds = [0, 60, 80, 100, 150]
cmap = plt.cm.RdYlGn_r


norm = Normalize(vmin=0, vmax=120)

sc = ax.scatter(
    sig_ax,
    sig_hoop,
    c=util_profile,
    cmap=cmap,
    norm=norm,
    s=25
)


cbar = plt.colorbar(sc, ax=ax)


cbar.set_ticks([0, 60, 80, 100, 120])
cbar.set_ticklabels(["0", "60", "80", "100", "120"])
util_pt = vm_crit / SMYS * 100
# Burst (Barlow)
burst_rating = 2 * SMYS * 1000 * t / OD

burst_util = max(
    0,
    (P_iny - Pext_surface) / burst_rating * 100
)

# Ballooning force
ballooning_lbf = (
    np.pi * ID**2 / 4
) * (P_iny - Pext_surface)
cbar.ax.plot(
    [0.5],
    [util_pt],
    marker='o',
    markersize=8,
    color='black'
)

cbar.ax.text(
    1.2,
    util_pt,
    f"{util_pt:.0f}%",
    va='center'
)


ratio = vm_crit / SMYS * 100

if ratio <= 60:
    color_pt = "#2ecc71"   # verde
elif ratio <= 80:
    color_pt = "#f1c40f"   # amarillo
elif ratio <= 100:
    color_pt = "#e67e22"   # naranja
else:
    color_pt = "#e74c3c"   # rojo

ax.scatter(
    sx,
    sy,
    color=color_pt,
    s=250,
    edgecolors="black",
    linewidths=2,
    zorder=10
)
# Aviso si falla por torque / VM total
# Aviso correcto según causa
if vm_crit > SMYS:
    if Torque > 0:
        txt = "FAIL (including torque)"
    else:
        txt = "FAIL (axial + pressure)"
    
    ax.text(
        0,
        SMYS * 0.85,
        txt,
        color="red",
        fontsize=12,
        fontweight="bold",
        ha="center"
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


max_val = max(
    np.max(np.abs(sig_ax)),
    np.max(np.abs(sig_hoop)),
    abs(sx),
    abs(sy)
)

lim = max(SMYS, max_val) * 1.2


ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

ax.set_aspect("equal")

ax.grid(True)

ax.set_xlabel("σ axial [ksi]")
ax.set_ylabel("σ hoop [ksi]")

st.pyplot(fig)

# =========================================
# TABLA VM
# =========================================

profundidades = np.arange(500, 5501, 500)
presiones = np.arange(0, 10000, 500)

tabla_vm = np.zeros((len(presiones), len(profundidades)))

for i_p, Piny in enumerate(presiones):
    for i_z, prof in enumerate(profundidades):

        tabla_vm[i_p, i_z] = calc_vm(
            prof,
            Piny,
            OD, ID, peso,
            rho_int, rho_ext,
            fill_int, fill_ext,
            Pext_surface,
            Torque, F_ext,
            Condition
        )

df_vm = pd.DataFrame(
    tabla_vm,
    index=[f"{p} psi" for p in presiones],
    columns=[f"{p} m" for p in profundidades]
)
# =========================================
# EXPANDER (CORRECTO)
# =========================================

# =========================================
# TITULO NUEVO (GRANDE Y NEGRITA)
# =========================================
st.markdown(
    "<h4 style='font-weight:400;'>📊 Sensitive Table: Inj Pressure Vs Depth | Content: Von Mises (KSI)</h4>",
    unsafe_allow_html=True)



with st.expander(" 🖲️Expand/Contract Table)", expanded=False):

   

    st.dataframe(
        df_vm.style
        .format("{:.1f}")
        .map(color_vm),
        use_container_width=False
    )

# =========================================
# BURST CHECK
# =========================================

t = (OD - ID) / 2

burst_api = 0.875 * 2 * YP * t / OD

burst_load = Pi - Po

burst_util = burst_load / burst_api * 100
# =========================================
# Conclusions
# =========================================
# =========================================
# BALLOONING
# =========================================

# =========================================
# BALLOONING
# =========================================

Pi = P_iny + rho_int * depth_ft * fill_int / 144
Po = Pext_surface + rho_ext * depth_ft * fill_ext / 144

if Condition == "Free":

    ballooning_lbf = 0

else:

    ballooning_lbf = (
        np.pi * ID**2 / 4
    ) * (Pi - Po)

ballooning_ksi = ballooning_lbf / A / 1000
st.subheader("Conclusions")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "σ axial [ksi]",
    round(sx,2)
)

c1.metric(
    "σ hoop [ksi]",
    round(sy,2)
)

c1.metric(
    "τ torque [ksi]",
    round(tau/1000, 2)
)

# color dinámico
color_vm = "green" if vm_crit < SMYS else "red"

# VON MISES CUSTOM
c2.markdown(f"""
<div style="
    background-color: #ffffff;
    border-radius: 10px;
    padding: 15px;
">
    <div style="font-size:14px;">Von Mises [ksi]</div>
    <div style="
        font-size:40px;
        font-weight:bold;
        color:{color_vm};
    ">
        {vm_crit:.1f}
    </div>
</div>
""", unsafe_allow_html=True)

burst_util = max(
    0,
    (Pi - Po) / burst_api * 100
)

collapse_util = max(
    0,
    (Po - Pi) / collapse_api * 100
)
fail_vm = vm_crit > SMYS

fail_burst = burst_util > 100

fail_collapse = collapse_util > 100

status = "FAIL" if (
    fail_vm
    or fail_burst
    or fail_collapse
) else "PASS"

c2.metric(
    "Estado",
    status
)
causas = []

if fail_vm:
    causas.append("Von Mises")

if fail_burst:
    causas.append("Burst")

if fail_collapse:
    causas.append("Collapse")

if len(causas) == 0:
    causas.append("None")

c2.metric(
    "Failure Mode",
    ", ".join(causas)
)
util = vm_crit / SMYS * 100

c3.metric(
    "Utilización [%]",
    round(util,1)
)



c3.metric(
    "Burst Utilization [%]",
    round(burst_util,1)
)
c3.metric(
    "Collapse Utilization [%]",
    round(collapse_util,1)
)
c3.metric(
    "Ballooning [lbf]",
    round(ballooning_lbf,0)
)






st.markdown(
    "<p style='font-size:11px; color:gray;'>"
    "Developed by FCAM & Pro-Eng - June 2026 "
   
    "</p>",
    unsafe_allow_html=True
)
st.markdown("---")

st.markdown("""
<div style="
font-size:11px;
color:#8a99a8;
text-align:center;
line-height:1.5;
padding-top:10px;
padding-bottom:20px;
">

<b>DISCLAIMER</b><br>

The calculations and results provided by this application are based on
industry-standard methodologies and API formulas applicable to tubulars
in new condition. For used, corroded, worn, damaged, or otherwise
degraded tubulars, the results should be considered for guidance
purposes only and shall not be used as the sole basis for operational,
engineering, or safety-critical decisions.

The user is solely responsible for verifying the suitability,
integrity, condition, and fitness-for-service of any equipment,
tubulars, or components evaluated using this software.
The developers, authors, and distributors of this application assume
no responsibility or liability for any losses, damages, operational
failures, injuries, or consequences arising from the use,
interpretation, or reliance upon the calculations presented herein.

Use of this application constitutes acceptance of these limitations.

</div>
""", unsafe_allow_html=True)

