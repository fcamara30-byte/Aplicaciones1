import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import imageio

# =========================
# PERFIL SINTÉTICO
# =========================

md = np.linspace(0, 800, 100)

inc = np.interp(md, [0,300,600,800],[0,20,35,35])
az = np.zeros_like(md)

inc_rad = np.radians(inc)

# Trayectoria simple
X = np.sin(inc_rad) * md * 0.1
Y = np.zeros_like(md)
Z = -md

# =========================
# DLS SIMPLE
# =========================
dls = np.gradient(inc) * 0.5

# =========================
# CONTACTO (modelo simple)
# =========================
T = md * 50
kappa = np.abs(dls) / 30

N = T * kappa

# normalizar para colores
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
# CREAR VIDEO
# =========================
frames = []

for i in range(60):

    fig = plt.figure(figsize=(6,8))
    ax = fig.add_subplot(111, projection='3d')

    # rotación
    ax.view_init(elev=20, azim=i*6)

    # tubo
    ax.plot(X, Y, Z, color='blue', linewidth=2, alpha=0.3)

    # sarta
    for j in range(len(X)-1):
        ax.plot(
            X[j:j+2],
            Y[j:j+2],
            Z[j:j+2],
            color=colors[j],
            linewidth=3
        )

    # zona crítica (parpadeo)
    size = 100 + 100*np.sin(i/5)
    ax.scatter(X[idx_crit], Y[idx_crit], Z[idx_crit],
               color='red', s=size)

    # =========================
    # TEXTO (PORTUGUÉS)
    # =========================

    if i < 15:
        texto = "Trajetória do poço"
    elif i < 30:
        texto = "Contato lateral das hastes"
    elif i < 45:
        texto = "Zona crítica de esforço"
    else:
        texto = "Torque e desgaste do sistema"

    ax.text2D(0.05, 0.95, texto,
              transform=ax.transAxes,
              fontsize=12,
              color='black')

    ax.set_xlim(-100,100)
    ax.set_ylim(-100,100)
    ax.set_zlim(-800,0)

    ax.set_axis_off()

    filename = f"frame_{i}.png"
    plt.savefig(filename)
    plt.close()

    frames.append(imageio.imread(filename))

# =========================
# EXPORT VIDEO
# =========================
imageio.mimsave("pcp_demo.mp4", frames, fps=10)

print("✅ Video generado: pcp_demo.mp4")
