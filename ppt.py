import numpy as np
import matplotlib.pyplot as plt
import imageio
import os
import streamlit as st

st.title("🎬 Demo PCP Animation")

# =========================
# PERFIL SIMPLE
# =========================
md = np.linspace(0, 800, 120)

inc = np.interp(md, [0,200,500,800], [0,10,35,35])
inc_rad = np.radians(inc)

# trayectoria
X = np.sin(inc_rad) * md * 0.15
Y = np.zeros_like(md)
Z = -md

# =========================
# CONTACTO
# =========================
dls = np.gradient(inc)
T = md * 40
kappa = np.abs(dls) / 30

N = T * kappa
N_norm = N / max(N)

# colores
colors = []
for n in N_norm:
    if n < 0.2:
        colors.append("green")
    elif n < 0.4:
        colors.append("yellow")
    elif n < 0.7:
        colors.append("orange")
    else:
        colors.append("red")

# zona crítica
idx_crit = np.argmax(N)

# =========================
# GENERAR ANIMACIÓN
# =========================

frames = []

st.write("⏳ Generando animación...")

for i in range(40):

    fig = plt.figure(figsize=(5,7))
    ax = fig.add_subplot(111, projection='3d')

    ax.view_init(elev=25, azim=i*6)

    # tubing
    ax.plot(X, Y, Z, color='blue', linewidth=2, alpha=0.3)

    # sarta
    for j in range(len(X)-1):
        ax.plot(
            X[j:j+2], Y[j:j+2], Z[j:j+2],
            color=colors[j], linewidth=3
        )

    # zona crítica
    ax.scatter(
        X[idx_crit], Y[idx_crit], Z[idx_crit],
        color='red', s=120
    )

    # texto portugués
    if i < 10:
        texto = "Trajetória do poço"
    elif i < 20:
        texto = "Contato lateral das hastes"
    elif i < 30:
        texto = "Zona crítica de carga"
    else:
        texto = "Torque e desgaste do sistema"

    ax.text2D(0.05, 0.9, texto, transform=ax.transAxes)

    ax.set_xlim(-150,150)
    ax.set_ylim(-150,150)
    ax.set_zlim(-800,0)

    ax.set_axis_off()

    filename = f"frame_{i}.png"
    plt.savefig(filename)
    plt.close()

    frames.append(imageio.imread(filename))

# =========================
# CREAR GIF
# =========================

gif_path = "pcp_demo.gif"
imageio.mimsave(gif_path, frames, fps=8)

# borrar frames
for i in range(40):
    os.remove(f"frame_{i}.png")

st.success("✅ Animación lista")

# =========================
# MOSTRAR GIF
# =========================
st.image(gif_path)

# =========================
# DESCARGA
# =========================
with open(gif_path, "rb") as f:
    st.download_button(
        label="⬇ Descargar animación",
        data=f,
        file_name="pcp_demo.gif",
        mime="image/gif"
    )
