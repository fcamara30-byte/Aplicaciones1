import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from modelo import *

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

# =========================================
# DEGRADACION
# =========================================
perdida_pct = st.sidebar.slider("Pérdida de espesor [%]", 0, 100, 0)
perdida = perdida_pct / 100

t_original = (OD - ID) / 2
t_actual = t_original * (1 - perdida)
ID = OD - 2 * t_actual

if t_actual <= 0:
    st.sidebar.error("Espesor nulo")

grado = st.sidebar.selectbox("Grado", ["J55","N80","P110","Q125"])
SMYS = {"J55":55,"N80":80,"P110":110,"Q125":125}[grado]

modo = st.sidebar.selectbox("Condición axial", ["Libre","Anclado","Packer"])
condicion = st.sidebar.selectbox("Condición Tubo", ["Abierto", "Cerrado"])

P_iny = st.sidebar.number_input("Presión de inyección [psi]", value=0.0)
Pext_surface = st.sidebar.number_input("Presión externa superficial [psi]", value=0.0)

rho_int_si = st.sidebar.number_input("ρ interno [kg/m³]", value=0.0)
rho_ext_si = st.sidebar.number_input("ρ externo [kg/m³]", value=0.0)

rho_int = kgm3_to_lbft3(rho_int_si)

