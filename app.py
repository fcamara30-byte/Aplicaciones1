import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *

st.set_page_config(layout="wide")
st.title("Von Mises OCTG")

# ----------------------------------------
# CONVERSIONES
# ----------------------------------------
def kgm3_to_lbft3(rho):
    return rho * 0.062428

def m_to_ft(z):
    return z * 3.28084

# ----------------------------------------
# BASE TUBOS (COMPLETA)
# ----------------------------------------
tubos = {
    "3 1/2 #9.2": (3.5, 0.254),
    "3 1/2 #7.7": (3.5, 0.216),
    "2 7/8 #6.4": (2.875, 0.254),
    "2 7/8 #4.04": (2.875, 0.177),
    "5 1/2 #15.5": (5.5, 0.275),
    "5 1/2 #10": (5.5, 0.231),
    "7 #23": (7.0, 0.317),
    "9 5/8 #36": (9.625, 0.395),
    "9 5/8 #43.5": (9.625, 0.545)
}

# ----------------------------------------
# INPUTS
# ----------------------------------------
st.sidebar.title("Inputs")

tubo = st.sidebar.selectbox("Tubing", list(tubos.keys()))
OD, t = tubos[tubo]
ID = OD - 2*t

grado = st.sidebar.selectbox("Grado", ["J55","N80","P110","Q125"])
yield_ksi = {"J55":55,"N80":80,"P110":110,"Q125":125}[grado]

modo = st.sidebar.selectbox("Condición axial", ["Libre","Anclado"])

rho_int = kgm3_to_lbft3(st.sidebar.number_input("ρ interno [kg/m³]",1050.0))
rho_ext = kgm3_to_lbft3(st.sidebar.number_input("ρ externo [kg/m³]",1050.0))

fill_int = st.sidebar.slider("Fill interno",0.0,1.0,1.0)
fill_ext = st.sidebar.slider("Fill externo",0.0,1.0,1.0)

Pint = st.sidebar.number_input("P interna [psi]",0.0)
Pext = st.sidebar.number_input("P externa [psi]",0.0)

Torque = st.sidebar.number_input("Torque [lb-ft]",0.0)
F_ext = st.sidebar.number_input("F axial [lbf]",0.0)

prof_ft = m_to_ft(st.sidebar.number_input("Profundidad [m]",3000.0))

# ----------------------------------------
# CALCULO
# ----------------------------------------
sig_ax = []
sig_hoop = []
vm_list = []

for i in range(200):

    z = prof_ft * i/200

    Pi = presion(z,Pint,rho_int,fill_int)
    Po = presion(z,Pext,rho_ext,fill_ext)

    hoop_i, rad_i = lame(Pi,Po,ID/2,OD/2,ID/2)
    hoop_o, rad_o = lame(Pi,Po,ID/2,OD/2,OD/2)

    ax_val = axial(z,OD,ID,rho_int,rho_ext,F_ext,Pi,Po,modo)
    tau = torsion(Torque,OD,ID)

    vm_i = VM(ax_val,hoop_i,rad_i,tau)
    vm_o = VM(ax_val,hoop_o,rad_o,tau)

    if vm_i > vm_o:
        sig_ax.append(ax_val/1000)
        sig_hoop.append(hoop_i/1000)
        vm_list.append(vm_i)
    else:
        sig_ax.append(ax_val/1000)
        sig_hoop.append(hoop_o/1000)
        vm_list.append(vm_o)

sig_ax = np.array(sig_ax)
sig_hoop = np.array(sig_hoop)
vm_list = np.array(vm_list)

# punto crítico
i_crit = np.argmax(vm_list)

ax_c = sig_ax[i_crit]
hoop_c = sig_hoop[i_crit]

# ----------------------------------------
# ELIPSE CORRECTA (SIN ERRORES)
# ----------------------------------------
s = np.linspace(-yield_ksi, yield_ksi, 2000)

x_valid = []
y_top = []
y_bot = []

for val in s:
    disc = 4*yield_ksi**2 - 3*val**2
    if disc >= 0:
        root = np.sqrt(disc)
        x_valid.append(val)
        y_top.append((val + root)/2)
        y_bot.append((val - root)/2)

x_vm = np.array(x_valid + x_valid[::-1])
y_vm = np.array(y_top + y_bot[::-1])

# ----------------------------------------
# PLOT
# ----------------------------------------
fig, ax = plt.subplots(figsize=(7,7))

# elipse
ax.plot(x_vm, y_vm, color="blue", lw=2)

# trayectoria
ax.plot(sig_ax, sig_hoop, color="orange", lw=2)

# punto crítico
ax.scatter(ax_c, hoop_c, color="red", s=120)

# ejes
ax.axhline(0, color='black', linewidth=1.5)
ax.axvline(0, color='black', linewidth=1.5)

# escala
lim = yield_ksi * 1.05
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)

# grilla
ticks = np.arange(-yield_ksi, yield_ksi+1, 10)
ax.set_xticks(ticks)
ax.set_yticks(ticks)

ax.grid(True, color='gray', linewidth=0.5)

ax.set_aspect("equal")

ax.set_xlabel("σ axial [ksi]")
ax.set_ylabel("σ hoop [ksi]")

st.pyplot(fig)

