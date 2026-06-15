import pandas as pd
from io import BytesIO
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import threading
import time
import requests


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

    if val < 0:
        return "background-color: #e74c3c"

    util = val / SMYS

    if util <= 0.6:
        return "background-color: #2ecc71"
    elif util <= 0.8:
        return "background-color: #f1c40f"
    elif util <= 1.0:
        return "background-color: #e67e22"
    else:
      return "background-color: #e74c3c"




st.set_page_config(layout="wide")
st.markdown("""
<style>
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0rem !important;
}
</style>
""", unsafe_allow_html=True)


def keep_alive():
    while True:
        try:
            requests.get("https://tubovonmisses.streamlit.app/")
            print("Self ping OK")
        except:
            print("Self ping failed")
        time.sleep(240)  # cada 4 minutos

threading.Thread(target=keep_alive, daemon=True).start()



st.markdown(
    """
    <h1 style="
        color:#0072CE;
        text-align:center;
        font-weight:bold;
    ">
    OCTG - Von Mises Calculation
    </h1>
    """,
    unsafe_allow_html=True
)

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

    # Geometría
    A = area_metal(OD, ID)
    ri = ID / 2
    ro = OD / 2
    t = (OD - ID) / 2

    A_ext_ft2 = (np.pi * OD**2 / 4) / 144

    # Presiones
    Pi = Piny + rho_int * depth_ft * fill_int / 144
    Po = Pext_surface + rho_ext * depth_ft * fill_ext / 144

    # Axial mecánico
    F_weight = peso * depth_ft

    F_buoy = rho_ext * A_ext_ft2 * z * fill_ext


    sigma_ax = (F_weight - F_buoy + F_ext) / A

    # Axial por presión
    if Condition == "Free":
        sigma_pressure = 0

    elif Condition == "Anchored":
        sigma_pressure = 0.5 * (
            (Pi * ri**2 - Po * ro**2)
            / (ro**2 - ri**2)
        )

    elif Condition == "Packer":
        sigma_pressure = (
            (Pi * ri**2 - Po * ro**2)
            / (ro**2 - ri**2)
        )

    else:
        sigma_pressure = 0

    # Axial total
    sa = sigma_ax + sigma_pressure

    # Hoop
    sh = (Pi - Po) * OD / (2 * t)

    # Torsión
    T = Torque * 12

    J = (np.pi / 2) * (ro**4 - ri**4)

    tau = T * ro / J if J > 0 else 0

    # Von Mises

    Sr=-Pi           
    vm = np.sqrt(
    (
        (sa - sh)**2 +
        (sh - sr)**2 +
        (sr - sa)**2
    ) / 2
    + 3 * tau**2
)

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
    '13 3/8" #54.5': (13.375, 12.615, 54.5),
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
burst_api = 0.875 * 2 * YP * t / OD
# SLENDERNESS PARAMETER
D_t = OD / t

if D_t < 20:
    collapse_api = 2 * YP * (t / OD)   # yield
elif D_t < 40:
    collapse_api = 0.875 * 2 * YP * (t / OD)  # plastic
else:
    collapse_api = 46.95e6 / (D_t**3)  # elastic simplificado


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
    value=1000.0,
    min_value=0.1,
    step=100.0,
    format="%.0f"

)

rho_ext = st.sidebar.number_input(
    "ρ Ext. [kg/m³]",
    value=1000.0,
     min_value=0.1,
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
    min_value=0.0,
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
    value=2000.0,
    min_value=0.0,
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
# =========================================
# GEOMETRIA (PRECOMPUTADA)
# =========================================
A = area_metal(OD, ID)
ri = ID / 2
ro = OD / 2
t = (OD - ID) / 2
A_ext_ft2 = (np.pi * OD**2 / 4) / 144


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
    # AXIAL MECANICO
    # ==========================
  

    F_weight = peso * z

    F_buoy = rho_ext * A_ext_ft2 * z * fill_ext


# distribución progresiva de carga externa (sin romper modelo)
    F_total = F_weight - F_buoy + F_ext


    sigma_ax = F_total / A

    # ==========================
    # AXIAL POR PRESION
    # ==========================
    if Condition == "Free":

        sigma_pressure = 0

    
    elif Condition == "Anchored":

      sigma_pressure = 0.5 * (
        Pi * ri**2
        - Po * ro**2
    ) / (
        ro**2 - ri**2
    )

    elif Condition == "Packer":

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
 

    sh = (
        (Pi - Po)
        * OD
        / (2*t)
    )

    # ==========================
    # RADIAL
    # ==========================
    sr = -Pi

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
# PRIMER FALLO
# =========================================
first_fail_index = None

for i in range(len(z_list)):

    z = z_list[i]

    z_int = z * fill_int
    z_ext = z * fill_ext

    Pi_i = P_iny + rho_int * z_int / 144
    Po_i = Pext_surface + rho_ext * z_ext / 144

    vm_i = vm_list[i]

    burst_util_i = max(0, (Pi_i - Po_i) / burst_api * 100)
    collapse_util_i = max(0, (Po_i - Pi_i) / collapse_api * 100)

    fail_vm_i = vm_i > SMYS
    fail_burst_i = burst_util_i > 100
    fail_collapse_i = collapse_util_i > 100

    if fail_vm_i or fail_burst_i or fail_collapse_i:

        first_fail_index = i

        if fail_burst_i:
            first_fail_mode = "Burst"
        elif fail_collapse_i:
            first_fail_mode = "Collapse"
        else:
            first_fail_mode = "VM"

        break   


if first_fail_index is not None:
    z_first_fail = ft_to_m(z_list[first_fail_index])
else:
    z_first_fail = None


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
disc = 4 * SMYS**2 - 3 * s**2
mask = disc >= 0

root = np.sqrt(disc[mask])

x_vm = s[mask]
y1 = (x_vm + root) / 2
y2 = (x_vm - root) / 2


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
ax.plot(
    sig_ax,
    sig_hoop,
    color="cyan",
    alpha=0.25,
    linewidth=1
)

cbar = plt.colorbar(
    sc,
    ax=ax,
    fraction=0.047,   # 👈 más angosta
    pad=0.03          # 👈 más cerca del gráfico
)


cbar.set_ticks([0, 60, 80, 100, 120])
cbar.set_ticklabels(["0", "60", "80", "100", "120"])
util_pt = vm_crit / SMYS * 100
# Burst (Barlow)
burst_rating = 2 * SMYS * 1000 * t / OD

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

# Ballooning force
ballooning_lbf = (np.pi * ID**2 / 4) * (Pi - Po)
cbar.ax.plot(
    [0.5],
    [util_pt],
    marker='o',
    markersize=6,
    color='black'
)


cbar.ax.text(
    -0.9,
    util_pt,
    f"{util_pt:.0f}%",
    va='center',
    fontsize=8,       
    color="blue",     
    fontweight='bold'
)



if fail_burst or fail_collapse:
    color_pt = "#e74c3c"

else:
    ratio = vm_crit / SMYS * 100

    if ratio <= 60:
        color_pt = "#2ecc71"
    elif ratio <= 80:
        color_pt = "#f1c40f"
    elif ratio <= 100:
        color_pt = "#e67e22"
    else:
        color_pt = "#e74c3c"


# glow externo
ax.scatter(
    sx, sy,
    s=600,
    color=color_pt,
    alpha=0.25,
    zorder=9
)

# punto real
ax.scatter(
    sx, sy,
    s=220,
    color=color_pt,
    edgecolors="white",
    linewidths=1.5,
    zorder=10
)

# Aviso si falla por torque / VM total
# Aviso correcto según causa
if fail_burst:
    txt = "FAIL - BURST"

elif fail_collapse:
    txt = "FAIL - COLLAPSE"

elif fail_vm:
    txt = "FAIL - VON MISES"

else:
    txt = ""

if txt != "":
    ax.text(
        0,
        SMYS * 0.85,
        txt,
        color="red",
        fontsize=14,
        fontweight="bold",
        ha="center"
    )

ax.annotate(
    f"VM={vm_crit:.1f} ksi",
    (sx, sy),
    xytext=(-60,15),   # 👈 clave: negativo en X
    textcoords="offset points",
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
tabla_fail = np.zeros((len(presiones), len(profundidades)))

for i_p, Piny in enumerate(presiones):

    for i_z, prof in enumerate(profundidades):

        depth_ft_tab = m_to_ft(prof)

        Pi_tab = (
            Piny
            + rho_int * depth_ft_tab * fill_int / 144
        )

        Po_tab = (
            Pext_surface
            + rho_ext * depth_ft_tab * fill_ext / 144
        )

        burst_util_tab = max(
            0,
            (Pi_tab - Po_tab) / burst_api * 100
        )

        collapse_util_tab = max(
            0,
            (Po_tab - Pi_tab) / collapse_api * 100
        )

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

        if (
            tabla_vm[i_p, i_z] > SMYS
            or burst_util_tab > 100
            or collapse_util_tab > 100
        ):
      
   
            tabla_fail[i_p, i_z] = 1





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

# BALLOONING
# =========================================

z_crit_ft = z_list[i_crit]

Pi = P_iny + rho_int * (z_crit_ft * fill_int) / 144
Po = Pext_surface + rho_ext * (z_crit_ft * fill_ext) / 144

if Condition == "Free":

    ballooning_lbf = 0

else:

    ballooning_lbf = (
        np.pi * ID**2 / 4
    ) * (Pi - Po)

ballooning_ksi = ballooning_lbf / A / 1000
st.subheader("Conclusions")

import plotly.graph_objects as go
import numpy as np

# =========================
# CONDICIONES
# =========================
hay_falla = (fail_vm or fail_burst or collapse_util > 100)


# =========================
# FUNCIÓN PRINCIPAL
# =========================
def tubo_pro(vm_list, SMYS, sa, sh, tau,
             fail_burst, collapse_util):

    n_theta = 40
    n_z = 60

    theta_1d = np.linspace(0, 2*np.pi, n_theta)
    z_vals = np.linspace(0, 10, n_z)

    theta, z = np.meshgrid(theta_1d, z_vals)

    R = 1.0

    r = np.ones_like(theta) * R

    modo = "None"

    if hay_falla:

        if collapse_util > 100:
            modo = "Collapse"

        elif fail_burst:
            modo = "Burst"

        else:
            valores = {
                "Axial": abs(sa),
                "Hoop": abs(sh),
                "Torque": abs(tau)
            }
            modo = max(valores, key=valores.get)

    # =========================
    # COLLAPSE
    # =========================
    if modo == "Collapse":

        mag = min(collapse_util / 150, 1.5)

        dent = np.exp(-((z - 5)**2)/1.2) * \
               np.exp(-((theta - np.pi/2)**2)/0.3)

        r = R - 0.6 * mag * dent

        x = r * np.cos(theta)
        y = r * np.sin(theta)

    # =========================
    # BURST
    # =========================
    elif modo == "Burst":

        deform = 1 + 1.3 * np.exp(-((z_vals - 5)**2)/2)
        r = deform.reshape(-1,1)

        x = r * np.cos(theta)
        y = r * np.sin(theta)

    # =========================
    # AXIAL
    # =========================
    elif modo == "Axial":

        signo = np.sign(sa)
        mag = min(abs(sa)/SMYS, 1.5)

        z = z * (1 + 1.2 * signo * mag)

        neck = np.exp(-((z_vals - 5)**2)/1.5)
        r = R * (1 - 0.4 * mag * neck.reshape(-1,1))

        x = r * np.cos(theta)
        y = r * np.sin(theta)

    # =========================
    # HOOP
    # =========================
    elif modo == "Hoop":

        signo = np.sign(sh)
        mag = min(abs(sh)/SMYS, 1.5)

        deform = 1 + signo * 1.2 * np.exp(-((z_vals - 5)**2)/2)
        r = deform.reshape(-1,1)

        x = r * np.cos(theta)
        y = r * np.sin(theta)

    # =========================
    # TORQUE ✅ HELICE REAL
    # =========================
    elif modo == "Torque":

        mag = min(abs(tau) / SMYS, 2.0)

        # torsión
        twist_max = np.pi * (2 + 4 * mag)
        twist = (z_vals / max(z_vals)) * twist_max

        theta_mod = theta + twist.reshape(-1,1)

        # patrón helicoidal a ~45°
        helix_pattern = np.sin(3 * theta_mod + 2 * z)

        radial_wave = 1 + 0.05 * mag * helix_pattern

        x = R * radial_wave * np.cos(theta_mod)
        y = R * radial_wave * np.sin(theta_mod)

    # =========================
    # COORDENADAS DEFAULT
    # =========================
    if modo != "Torque":
        x = r * np.cos(theta)
        y = r * np.sin(theta)

    # =========================
    # COLOR
    # =========================
    vm_norm = np.clip(vm_list / SMYS, 0, 1)

    vm_small = np.interp(
        np.linspace(0, len(vm_list)-1, n_z),
        np.arange(len(vm_list)),
        vm_norm
    )

    color = np.tile(vm_small.reshape(-1,1), (1, n_theta))

    # =========================
    # GRAFICO
    # =========================
    fig = go.Figure()

    fig.add_trace(go.Surface(
        x=x,
        y=y,
        z=z,
        surfacecolor=color,
        colorscale="RdYlGn_r",
        showscale=False,

        lighting=dict(
            ambient=0.25,
            diffuse=0.9,
            specular=1.0,
            roughness=0.25,
            fresnel=0.6
        ),

        lightposition=dict(
            x=200,
            y=150,
            z=180
        )
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        height=300,
        width=280,

        scene=dict(
            aspectratio=dict(x=1, y=1, z=2.5),
            camera=dict(
                eye=dict(x=2.2, y=2.0, z=1.5)
            ),
            xaxis_visible=False,
            yaxis_visible=False,
            zaxis_visible=False
        )
    )

    return fig







# =========================
# RENDER
# =========================
# =========================
# LAYOUT: RESULTADOS + 3D
# =========================
util = vm_crit / SMYS * 100
status = "FAIL" if (fail_vm or fail_burst or collapse_util > 100) else "PASS"




col_left, col_right = st.columns([2.3, 1])

# =========================
# IZQUIERDA (TODO JUNTO ARRIBA ✅)
# =========================
with col_left:

    c1, c2, c3, c4 = st.columns(4)

    # columna 1
    with c1:
        st.metric("σ axial [ksi]", round(sx,1))
        st.metric("σ hoop [ksi]", round(sy,1))
        st.metric("τ torque [ksi]", round(tau/1000,1))

    # columna 2
    with c2:
        color_vm = "green" if vm_crit < SMYS else "red"
        st.markdown(f"""
        <div style="background-color:#fff; border-radius:10px; padding:15px;">
            <div style="font-size:14px;">Von Mises [ksi]</div>
            <div style="font-size:40px; font-weight:bold; color:{color_vm};">
                {vm_crit:.1f}
            </div>
        </div>
        """, unsafe_allow_html=True)

        status = "FAIL" if (fail_vm or fail_burst or collapse_util > 100) else "PASS"
        color_estado = "red" if status == "FAIL" else "green"

        st.markdown(f"""
        <div style="background-color:#fff; border-radius:10px; padding:15px;">
            <div style="font-size:14px;">Estado</div>
            <div style="font-size:42px; font-weight:900; color:{color_estado};">
                {status}
            </div>
        </div>
        """, unsafe_allow_html=True)

        causas = []
        if fail_vm: causas.append("VM")
        if fail_burst: causas.append("Burst")
        if fail_collapse: causas.append("Coll")
        if not causas: causas.append("None")

        st.metric("Failure Mode", ", ".join(causas))

    # columna 3
    with c3:
        util = vm_crit / SMYS * 100
        color_vm_util = "red" if util > 100 else "black"

        st.markdown(f"""
        <div style="background-color:#fff; border-radius:10px; padding:15px;">
            <div style="font-size:14px;">VM Utilization [%]</div>
            <div style="font-size:38px; font-weight:bold; color:{color_vm_util};">
                {util:.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

        burst_util = max(0, (Pi - Po) / burst_api * 100)
        color_burst = "red" if burst_util > 100 else "black"

        st.markdown(f"""
        <div style="background-color:#fff; border-radius:10px; padding:15px;">
            <div style="font-size:14px;">Burst Utilization [%]</div>
            <div style="font-size:38px; font-weight:bold; color:{color_burst};">
                {burst_util:.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # columna 4
    with c4:
        collapse_util = max(0, (Po - Pi) / collapse_api * 100)

        st.metric("Collapse Util [%]", round(collapse_util,1))
        st.metric("Ballooning [Klb]", f"{ballooning_lbf/1000:.0f}")


# =========================
# DERECHA (SIMULATION)
# =========================
with col_right:


    st.plotly_chart(
        tubo_pro(
            vm_list,
            SMYS,
            sx,
            sy,
            tau/1000,
            fail_burst,
            collapse_util
        ),
        use_container_width=False
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
rodolfo.alves@tubosapolo.com.br // federico.camara@tubosapolo.com.br //   https://tubosapolo.com.br/ 

</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.image("https://flagcdn.com/w40/br.png")

with col2:
    st.image("https://flagcdn.com/w40/ar.png")
