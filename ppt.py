import numpy as np
import matplotlib.pyplot as plt
import imageio

# =========================
# PERFIL SIMPLE (pozo sintético)
# =========================

md = np.linspace(0, 800, 120)

inc = np.interp(md, [0,200,500,800], [0,10,35,35])
inc_rad = np.radians(inc)

# Trayectoria
X = np.sin(inc_rad) * md * 0.15
Y = np.zeros_like(md)
Z = -md

# =========================
# CONTACTO SIMPLE
# =========================

dls = np.gradient(inc)
T = md * 40
kappa = np.abs(dls) / 30

N = T * kappa
N_norm = N / max(N)

# =========================
# COLORES
# =========================

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
# CREAR ANIMACIÓN
# =========================

frames = []

for i in range(60):

    fig = plt.figure(figsize=(6,8))
    ax = fig.add_subplot(111, projection='3d')

    # rotación
    ax.view_init(elev=25, azim=i*4)

    # tubing (traslúcido)
    ax.plot(X, Y, Z, color='blue', linewidth=2, alpha=0.3)

    # sarta (coloreada)
    for j in range(len(X)-1):
        ax.plot(
            X[j:j+2],
            Y[j:j+2],
            Z[j:j+2],
            color=colors[j],
            linewidth=3
        )

    # zona crítica (pulse)
    size = 80 + 80*np.sin(i/4)
    ax.scatter(
        X[idx_crit], Y[idx_crit], Z[idx_crit],
        color='red', s=size
    )

    # =========================
    # TEXTO EN PORTUGUÉS
    # =========================

    if i < 15:
        texto = "Trajetória do poço"
    elif i < 30:
        texto = "Contato lateral gerado pela curvatura"
    elif i < 45:
        texto = "Zona crítica de maior carga"
    else:
        texto = "Torque e desgaste do sistema PCP"

    ax.text2D(
        0.05, 0.95, texto,
        transform=ax.transAxes,
        fontsize=12,
        color='black'
    )

    ax.set_xlim(-150,150)
    ax.set_ylim(-150,150)
    ax.set_zlim(-800,0)

    ax.set_axis_off()

    # guardar frame
    filename = f"frame_{i}.png"
    plt.savefig(filename)
    plt.close()

    frames.append(imageio.imread(filename))

# =========================
# EXPORT GIF
# =========================

imageio.mimsave("pcp_demo.gif", frames, fps=10)

print("✅ GIF generado: pcp_demo.gif")
