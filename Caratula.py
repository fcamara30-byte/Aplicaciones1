import streamlit as st

st.set_page_config(
    page_title="Petroleum Engineering Hub",
    page_icon="⚙️",
    layout="wide"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background:
    linear-gradient(
        135deg,
        #07111f 0%,
        #0c1f36 40%,
        #081220 100%
    );
}

/* Oculta menú streamlit */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

/* HERO */

.hero {
    text-align:center;
    padding-top:30px;
    padding-bottom:40px;
}

.hero-icon {
    font-size:80px;
}

.hero-title {
    font-size:64px;
    font-weight:800;
    color:white;
    letter-spacing:2px;
    margin-bottom:10px;
}

.hero-subtitle {
    font-size:24px;
    color:#9fb3c8;
    margin-bottom:15px;
}

.hero-line {
    width:200px;
    height:4px;
    background:#2ea8ff;
    margin:auto;
    border-radius:10px;
}

/* SECTION TITLE */

.section-title {
    color:white;
    font-size:34px;
    font-weight:700;
    margin-top:40px;
    margin-bottom:20px;
}

/* CARDS */

.card {
    background:
    linear-gradient(
        160deg,
        #16243a,
        #0d1728
    );

    border:1px solid #223a58;
    border-radius:25px;

    padding:35px;

    min-height:280px;

    transition:0.3s;
}

.card:hover {
    transform:translateY(-8px);
    box-shadow:0px 0px 35px rgba(46,168,255,0.35);
}

.card-icon {
    font-size:55px;
    text-align:center;
}

.card-title {
    color:white;
    text-align:center;
    font-size:38px;
    font-weight:700;
    margin-top:15px;
}

.card-desc {
    color:#b5c5d6;
    text-align:center;
    font-size:20px;
    margin-top:15px;
}

/* Papers */

.paper {
    background:#111c2f;
    border-left:5px solid #2ea8ff;
    border-radius:10px;
    padding:15px;
    margin-bottom:12px;
    color:white;
}

/* Footer */

.footer {
    text-align:center;
    color:#8aa1b7;
    margin-top:50px;
    margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HERO
# =====================================================

st.markdown("""
<div class="hero">

<div class="hero-icon">⚙️</div>

<div class="hero-title">
PETROLEUM ENGINEERING HUB
</div>

<div class="hero-subtitle">
OCTG • Artificial Lift • Reliability • Integrity
</div>

<div class="hero-line"></div>

</div>
""", unsafe_allow_html=True)

# =====================================================
# APPLICATIONS
# =====================================================

st.markdown(
    '<div class="section-title">Engineering Applications</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    st.markdown("""
    <div class="card">
        <div class="card-icon">🛢️</div>
        <div class="card-title">
            Von Mises Tube Analyzer
        </div>

        <div class="card-desc">
            OCTG Stress Envelope<br>
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

with col2:

    st.markdown("""
    <div class="card">
        <div class="card-icon">⚙️</div>
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

with col3:

    st.markdown("""
    <div class="card">
        <div class="card-icon">📈</div>
        <div class="card-title">
            Goodman Fatigue Assessment
        </div>

        <div class="card-desc">
            Fatigue Analysis<br>
            Goodman Diagram<br>
            Rod Reliability
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "ENTER PLATFORM →",
        "https://selectorvarillas.streamlit.app/",
        use_container_width=True
    )

with col4:

    st.markdown("""
    <div class="card">
        <div class="card-icon">🔩</div>
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

# =====================================================
# LIBRARY
# =====================================================

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
📄 Rod Fatigue Assessment using Goodman Criteria
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="paper">
📄 Artificial Lift Optimization Techniques
</div>
""", unsafe_allow_html=True)

# =====================================================
# FOOTER
# =====================================================

st.markdown("""
<div class="footer">

Petroleum Engineering Hub v2.0

<br>

OCTG • PCP • SRP • Integrity Engineering

</div>
""", unsafe_allow_html=True)
