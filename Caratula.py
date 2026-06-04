import streamlit as st
from pathlib import Path

VISIT_FILE = "visits.txt"

if not Path(VISIT_FILE).exists():
    with open(VISIT_FILE, "w") as f:
        f.write("0")

# ==========================================================
# CONFIG
# ==========================================================

st.set_page_config(
    page_title="Quick Calculation Guide",
    page_icon="⚙",
    layout="wide"
)
try:

    with open(VISIT_FILE, "r") as f:
        contenido = f.read().strip()

    visitas = int(contenido)

except:

    visitas = 0

visitas += 1

with open(VISIT_FILE, "w") as f:
    f.write(str(visitas))
# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>

.stApp{
    background:
    linear-gradient(
        135deg,
        #07111f 0%,
        #0d2038 50%,
        #07111f 100%
    );
}

/* Ocultar Streamlit */

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

/* HERO */

.hero{
    text-align:center;
    padding-top:20px;
    padding-bottom:40px;
}

.hero-title{
    font-size:90px;
    font-weight:900;
    color:white;
    line-height:0.9;
}

.hero-title2{
    font-size:90px;
    font-weight:900;
    color:#4db8ff;
    line-height:0.9;
}

.hero-sub{
    margin-top:25px;
    color:#b5c5d6;
    font-size:24px;
    letter-spacing:2px;
}

.hero-line{
    width:250px;
    height:4px;
    background:#4db8ff;
    margin:auto;
    margin-top:20px;
    border-radius:10px;
}

/* SECTION */

.section-title{
    color:white;
    font-size:34px;
    font-weight:700;
    margin-top:30px;
    margin-bottom:20px;
}

/* CARDS */

.card{
    background:
    linear-gradient(
        135deg,
        #152842,
        #0c1829
    );

    border:1px solid #21476f;

    border-radius:30px;

    padding:35px;

    min-height:260px;

    transition:0.3s;
}

.card:hover{
    transform:translateY(-6px);

    box-shadow:
    0px 0px 25px
    rgba(77,184,255,0.35);
}

.card-icon{
    text-align:center;
    font-size:60px;
}

.card-title{
    text-align:center;
    color:white;
    font-size:34px;
    font-weight:800;
    margin-top:15px;
}

.card-desc{
    text-align:center;
    color:#c4d1df;
    font-size:18px;
    line-height:1.7;
    margin-top:20px;
}

/* LIBRARY */

.paper{
    background:#122036;

    border-left:5px solid #4db8ff;

    padding:18px;

    border-radius:10px;

    color:white;

    margin-bottom:12px;
}

/* FOOTER */

.footer{
    text-align:center;
    color:#9db1c5;
    margin-top:40px;
    margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# HERO
# ==========================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
ONSHORE
</div>

<div class="hero-title2">
Quick Calculation Guide
</div>

<div class="hero-sub">
OCTG • ARTIFICIAL LIFT • CORROSION FATIGUE
</div>

<div class="hero-line"></div>

</div>
""", unsafe_allow_html=True)

# ==========================================================
# APPLICATIONS
# ==========================================================

st.markdown(
    '<div class="section-title">Engineering Applications</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

# ==========================================================
# CARD 1
# ==========================================================

with col1:

    st.markdown("""
    <div class="card">

    <div class="card-icon">
    🛢
    </div>

    <div class="card-title">
    Von Mises Tube Analyzer
    </div>

    <div class="card-desc">
    OCTG Stress <br>
    Yield Assessment<br>
    Design Verification
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "ENTER PLATFORM →",
        "https://tubovonmisses.streamlit.app/",
        use_container_width=True
    )

# ==========================================================
# CARD 2
# ==========================================================

with col2:

    st.markdown("""
    <div class="card">

    <div class="card-icon">
    ⚙
    </div>

    <div class="card-title">
    PCP String Stress Analysis
    </div>

    <div class="card-desc">
    Torque Evaluation<br>
    Tensile Loads<br>
    PCP Design
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "ENTER PLATFORM →",
        "https://pcpsuckerod.streamlit.app/",
        use_container_width=True
    )

st.write("")

col3, col4 = st.columns(2)

# ==========================================================
# CARD 3
# ==========================================================

with col3:

    st.markdown("""
    <div class="card">

    <div class="card-icon">
    📈
    </div>

    <div class="card-title">
    Goodman Fatigue Assessment
    </div>

    <div class="card-desc">
    Fatigue Evaluation<br>
    Goodman Diagram<br>
    Suggestions
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "ENTER PLATFORM →",
        "https://selectorvarillas.streamlit.app/",
        use_container_width=True
    )

# ==========================================================
# CARD 4
# ==========================================================

with col4:

    st.markdown("""
    <div class="card">

    <div class="card-icon">
    📅
    </div>
    <div class="card-title">
    Rod String Design
    </div>

    <div class="card-desc">
    Beam Pump Design<br>
    Rod Loads<br>
    Production Optimization
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "ENTER PLATFORM →",
        "https://calculoapi.streamlit.app/",
        use_container_width=True
    )

# ==========================================================
# LIBRARY
# ==========================================================

st.markdown(
    '<div class="section-title">Technical Library</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="paper">
📄 CO₂ Corrosion Mechanisms in OCTG
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="paper">
📄 PCP Failure Analysis and Design Practices
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="paper">
📄 Goodman Fatigue Assessment for Sucker Rods
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="paper">
📄 Artificial Lift Optimization Techniques
</div>
""", unsafe_allow_html=True)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("""
<div class="footer">
Developed by FCAM & Pro-Eng

<br><br>

OCTG • PCP • SRP 

</div>
""", unsafe_allow_html=True)
st.markdown("---")

st.markdown(
    f"""
    <div style="
        text-align:center;
        color:#9db1c5;
        font-size:18px;
        margin-top:15px;
        margin-bottom:20px;
    ">
        👁️ Total Visits: <b>{visitas:,}</b>
    </div>
    """,
    unsafe_allow_html=True
)
