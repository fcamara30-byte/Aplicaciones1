
import streamlit as st
import matplotlib.pyplot as plt

from modelo import *


# ---------------------------
# TITULO
# ---------------------------
st.title("Modelo Von Mises - Tubing")


# ---------------------------
# INPUTS
# ---------------------------
st.sidebar.header("Inputs")

OD = st.sidebar.number_input("OD (in)", value=2.875)
ID = st.sidebar.number_input("ID (in)", value=2.441)

yield_ksi = st.sidebar.number_input("Yield (ksi)", value=64.0)

rho_int = st.sidebar.number_input("Densidad interna (kg/m3)", value=1050)
rho_ext = st.sidebar.number_input("Densidad externa (kg/m3)", value=1200)

fill_int = st.sidebar.slider("Fill interno", 0.0, 1.0, 1.0)
fill_ext = st.sidebar.slider("Fill externo", 0.0, 1.0, 1.0)

Pint_surface = st.sidebar.number_input("P interna superficie (psi)", value=1500.0)
Pext_surface = st.sidebar.number_input("P externa superficie (psi)", value=0.0)

prof_max = st.sidebar.number_input("Profundidad (m)", value=2000)


# ---------------------------
# CALCULO
# ---------------------------
if st.button("Calcular"):

    zs = []
    ratios = []

    peor_ratio = 0
    peor_z = 0

    for i in range(100):
        z = prof_max * i / 100

        Pint = presion(z, Pint_surface, rho_int, fill_int)
        Pext = presion(z, Pext_surface, rho_ext, fill_ext)

        DeltaP = Pint - Pext

        sig_hoop = tension_circunferencial(DeltaP, OD, ID)
        sig_ax = tension_axial(z, OD, ID, rho_int, rho_ext)

        vm = von_mises(sig_ax, sig_hoop)

        ratio = vm / yield_ksi

        zs.append(z)
        ratios.append(ratio)

        if ratio > peor_ratio:
            peor_ratio = ratio
            peor_z = z


    # ---------------------------
    # RESULTADOS
    # ---------------------------
    st.subheader("Resultados")

    st.write(f"Profundidad crítica: {round(peor_z,2)} m")
    st.write(f"Ratio VM: {round(peor_ratio,3)}")

    if peor_ratio > 1:
        st.error("FALLA")
    elif peor_ratio > 0.9:
        st.warning("CERCA DEL LÍMITE")
    else:
        st.success("SEGURO")


    # ---------------------------
    # GRAFICO
    # ---------------------------
    fig, ax = plt.subplots()

    ax.plot(zs, ratios)
    ax.set_xlabel("Profundidad (m)")
    ax.set_ylabel("VM / admisible")
    ax.grid()

    st.pyplot(fig)
