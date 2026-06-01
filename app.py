import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ✅ TITULO (sin tubing)
st.title("Diagrama Von Mises")

# -----------------------------
# PARÁMETRO
# -----------------------------
yield_ksi = st.sidebar.number_input("Yield (ksi)", value=80.0)

# -----------------------------
# ELIPSE (FORMA CORRECTA)
# -----------------------------
theta = np.linspace(0, 2*np.pi, 2000)

# ✅ parametrización robusta (SIEMPRE CIERRA)
sigma_ax = yield_ksi * (np.cos(theta))
sigma_hoop = yield_ksi * (np.sin(theta) - 0.5*np.cos(theta))

# -----------------------------
# PUNTO DE EJEMPLO (para probar)
# -----------------------------
ax_point = 10
hoop_point = 8

# -----------------------------
# PLOT
# -----------------------------
fig, ax = plt.subplots(figsize=(7,7))

# ✅ elipse
ax.plot(sigma_ax, sigma_hoop, color="blue", linewidth=2)

# ✅ punto
ax.scatter(ax_point, hoop_point, color="red", s=120)

# -----------------------------
# LIMITES (líneas rojas)
# -----------------------------
lim = yield_ksi

ax.axvline(lim, color="red", linestyle="--")
ax.axvline(-lim, color="red", linestyle="--")
ax.axhline(lim, color="red", linestyle="--")
ax.axhline(-lim, color="red", linestyle="--")

# -----------------------------
# EJES
# -----------------------------
ax.axhline(0, color="black")
ax.axvline(0, color="black")

ax.set_xlim(-lim*1.2, lim*1.2)
ax.set_ylim(-lim*1.2, lim*1.2)

ax.set_aspect("equal")

ax.set_xlabel("σ axial (ksi)")
ax.set_ylabel("σ circunferencial (ksi)")

ax.grid()

st.pyplot(fig)
