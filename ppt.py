import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("Simulación Física PCP - Trayectoria y Desgaste")

# 1. GENERAR DATOS SIMULADOS DEL POZO (Simulando tu archivo Survey)
# Creamos una trayectoria curva (un pozo desviado)
z = np.linspace(0, 100, 100)  # Profundidad
x = np.sin(z / 10) * 5         # Desvío en X
y = np.cos(z / 20) * 3         # Desvío en Y

# 2. CALCULAR PUNTOS DE CONTACTO / CENTRALIZADORES
# Simulamos que en ciertas profundidades ponemos centralizadores (puntos verdes)
centralizadores_z = [20, 50, 80]
centralizadores_x = [np.sin(cz / 10) * 5 for cz in centralizadores_z]
centralizadores_y = [np.cos(cz / 20) * 3 for cz in centralizadores_z]

# 3. ARMAR EL GRÁFICO 3D CON PLOTLY
fig = go.Figure()

# Dibujar la Tubería (Tubing)
fig.add_trace(go.Scatter3d(
    x=x, y=y, z=z,
    mode='lines',
    line=dict(color='gray', width=8),
    name='Tubing (Tubería)'
))

# Dibujar la Varilla de Bombeo (Rod)
fig.add_trace(go.Scatter3d(
    x=x, y=y, z=z,
    mode='lines',
    line=dict(color='red', width=3),
    name='Varilla (Zona de Fricción)'
))

# Dibujar los Centralizadores
fig.add_trace(go.Scatter3d(
    x=centralizadores_x, y=centralizadores_y, z=centralizadores_z,
    mode='markers',
    marker=dict(color='green', size=8, symbol='diamond'),
    name='Centralizadores Optimizados'
))

# Configuración de la vista 3D (ejes, rotación, etc.)
fig.update_layout(
    scene=dict(
        xaxis_title='Desvío X (m)',
        yaxis_title='Desvío Y (m)',
        zaxis_title='Profundidad (m)',
        zaxis=dict(autorange="reverse") # Los pozos van hacia abajo
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    height=600
)

# 4. MOSTRARLO EN STREAMLIT
# Esto renderiza el gráfico interactivo en 3D que podés girar con el mouse
st.plotly_chart(fig, use_container_width=True)
