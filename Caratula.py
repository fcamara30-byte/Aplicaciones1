import streamlit as st

st.set_page_config(
    page_title="Engineering Hub",
    page_icon="⚙️",
    layout="wide"
)

st.markdown("""
<style>

.main {
    background: linear-gradient(
        135deg,
        #0f172a,
        #1e293b
    );
}

.title {
    text-align:center;
    color:white;
    font-size:42px;
    font-weight:700;
}

.subtitle {
    text-align:center;
    color:#cbd5e1;
    font-size:18px;
    margin-bottom:40px;
}

.card {
    background-color:#1e293b;
    padding:25px;
    border-radius:20px;
    border:1px solid #334155;
    text-align:center;
    height:220px;
}

.card h2{
    color:white;
}

.card p{
    color:#cbd5e1;
}

.stButton button{
    width:100%;
    height:50px;
    border-radius:10px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="title">⚙️ Engineering Hub</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">OCTG & Artificial Lift Engineering Suite</div>',
    unsafe_allow_html=True
)

col1,col2 = st.columns(2)

with col1:

    st.markdown("""
    <div class="card">
    <h2>🛢️ Von Mises en Tubos</h2>
    <p>Diseño OCTG bajo criterio Von Mises</p>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "Abrir Aplicación",
        "https://tubovonmisses.streamlit.app/"
    )

with col2:

    st.markdown("""
    <div class="card">
    <h2>⚙️ Tensiones Sistema BCP</h2>
    <p>Cálculo de esfuerzos en sarta PCP</p>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "Abrir Aplicación",
        "https://pcpsuckerod.streamlit.app/"
    )

col3,col4 = st.columns(2)

with col3:

    st.markdown("""
    <div class="card">
    <h2>📈 Tensiones Goodman</h2>
    <p>Evaluación de fatiga en varillas</p>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "Abrir Aplicación",
        "https://selectorvarillas.streamlit.app/"
    )

with col4:

    st.markdown("""
    <div class="card">
    <h2>🔧 Bombeo Mecánico</h2>
    <p>Dimensionamiento y cálculo de varillas</p>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "Abrir Aplicación",
        "https://calculoapi.streamlit.app/"
    )

st.divider()

st.header("📚 Papers Técnicos")

st.info(
    """
    Próximamente:
    - Corrosión CO₂
    - Diseño OCTG
    - Fatiga de varillas
    - BCP y Bombeo Mecánico
    """
)

st.divider()

st.caption(
    "Engineering Suite v1.0 | Federico CG"
)
