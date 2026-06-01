
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

    # ---------------------------
    # CALCULO EN PROFUNDIDAD
    # ---------------------------
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
    # GRAFICO ELIPSE VON MISES
    # ---------------------------
    fig2, ax2 = plt.subplots()

    sigma_ax_vals = []
    sigma_hoop_vals = []

    # Construcción correcta de la elipse VM
    for i in range(-100, 100):
        s_ax = yield_ksi * i / 100

        # discriminante
        disc = 4*yield_ksi**2 - 3*s_ax**2

        if disc >= 0:
            root = (disc)**0.5

            # dos ramas (elipse completa)
            s_hoop1 = (s_ax + root)/2
            s_hoop2 = (s_ax - root)/2

            sigma_ax_vals.append(s_ax)
            sigma_hoop_vals.append(s_hoop1)

            sigma_ax_vals.append(s_ax)
            sigma_hoop_vals.append(s_hoop2)

    # dibujar elipse
    ax2.scatter(sigma_ax_vals, sigma_hoop_vals, s=5, label="Envolvente VM")


    # ---------------------------
    # PUNTO OPERATIVO (CRITICO)
    # ---------------------------
    Pint = presion(peor_z, Pint_surface, rho_int, fill_int)
    Pext = presion(peor_z, Pext_surface, rho_ext, fill_ext)

    DeltaP = Pint - Pext

    sig_hoop = tension_circunferencial(DeltaP, OD, ID)
    sig_ax = tension_axial(peor_z, OD, ID, rho_int, rho_ext)

    ax2.scatter(sig_ax, sig_hoop, color="red", s=120, label="Punto crítico")


    # ---------------------------
    # FORMATO
    # ---------------------------
ax2.set_xlabel("σ axial (ksi)")
ax2.set_ylabel("σ circumferencial (ksi)")

# 🔥 Escala correcta (CLAVE)
ax2.set_aspect('equal', adjustable='box')

# 🔥 Límites simétricos (para cerrar la elipse)
lim = yield_ksi * 1.2
ax2.set_xlim(-lim, lim)
ax2.set_ylim(-lim, lim)

# 🔥 Líneas eje
ax2.axhline(0, color='black', linewidth=1)
ax2.axvline(0, color='black', linewidth=1)

ax2.legend()
ax2.grid()


    st.pyplot(fig2)
