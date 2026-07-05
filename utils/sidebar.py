import streamlit as st
from utils.prefs import load_prefs, save_prefs, save_col_order, COLUMN_DEFAULTS
from utils.data import TIPO_COLORS, STATO_COLORS

SIDEBAR_CSS = """
<style>
[data-testid="stSidebar"] {
    min-width: 210px !important;
    max-width: 210px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
[data-testid="stSidebar"] * {
    font-size: 12px !important;
}

/* Legenda pallini: spazio verticale leggibile */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    margin: 4px 0 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Separatori compatti */
[data-testid="stSidebar"] hr {
    margin: 4px 0 !important;
}

/* Titoli sezione */
[data-testid="stSidebar"] strong {
    font-size: 12px !important;
}

/* Checkbox: compressi */
[data-testid="stSidebar"] .stCheckbox {
    margin-bottom: -10px !important;
}
[data-testid="stSidebar"] .stCheckbox label {
    font-size: 11px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 185px !important;
}

/* Bottone Logout: più spazio sopra */
[data-testid="stSidebar"] .stButton {
    margin-top: 10px !important;
}
[data-testid="stSidebar"] .stButton button {
    font-size: 12px !important;
}
</style>
"""

# CSS compatto anche per pagina principale
PAGE_CSS = """
<style>
/* Pagina: padding minimo */
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 0 !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}
div[data-testid="stVerticalBlock"] > div { gap: 0.15rem !important; }
h1, h2, h3 { margin: 0 !important; }
hr { margin: 0.2rem 0 !important; }
div[data-testid="stAlert"] { padding: 0.25rem 0.6rem !important; font-size: 12px !important; }
div[data-testid="stSelectbox"] { margin-bottom: 0 !important; }

/* Testo markdown generico */
div[data-testid="stMarkdownContainer"] p { margin: 0 !important; font-size: 12px !important; }
details { margin: 0 !important; }
summary { padding: 0.2rem 0 !important; font-size: 12px !important; }

/* Griglia AgGrid */
iframe[title="st_aggrid.agGrid"] {
    height: calc(100vh - 220px) !important;
    min-height: 300px !important;
}

/* Centra header Tipo e Stato */
.ag-header-cell[col-id="Tipo"] .ag-header-cell-label,
.ag-header-cell[col-id="Stato"] .ag-header-cell-label,
.ag-header-cell[col-id="Tipo_Icon"] .ag-header-cell-label,
.ag-header-cell[col-id="Stato_Icon"] .ag-header-cell-label {
    justify-content: center;
}


/* Bottone Reset: colonna che contiene il marcatore .reset-marker */
[data-testid="stColumn"]:has(.reset-marker) button {
    background-color: #C00000 !important;
    color: white !important;
    border: none !important;
}
[data-testid="stColumn"]:has(.reset-marker) button:hover {
    background-color: #9B0000 !important;
    color: white !important;
}

/* Nasconde toolbar nativa data_editor / dataframe */
[data-testid="stElementToolbar"] { display: none !important; }

/* Nasconde navigazione automatica Streamlit */
[data-testid="stSidebarNav"] { display: none !important; }

</style>
"""


def render_sidebar(role: str, resp_name: str, prefs: dict, col_order: list, page: str = "dashboard") -> bool:
    """Renders sidebar and returns True if prefs changed."""
    st.markdown(SIDEBAR_CSS + PAGE_CSS, unsafe_allow_html=True)

    with st.sidebar:
        if st.button("🏠 Homepage",  use_container_width=True, key="nav_home"):
            st.switch_page("streamlit_app.py")
        if st.button("📊 Dashboard", use_container_width=True, key="nav_dash"):
            st.switch_page("pages/1_Dashboard.py")
        if role == "owner":
            if st.button("✏️ Modifica", use_container_width=True, key="nav_mod"):
                st.switch_page("pages/2_Modifica.py")
            if st.button("🔧 Admin",    use_container_width=True, key="nav_adm"):
                st.switch_page("pages/3_Admin.py")
        st.markdown("---")
        st.markdown(f"**{resp_name}**")
        st.markdown(f"_{('Owner' if role == 'owner' else 'Project Manager')}_")
        st.markdown("---")

        st.markdown("**Tipo Attività**")
        for label, icon in TIPO_COLORS.items():
            st.markdown(f"{icon} {label}")
        st.markdown("---")

        st.markdown("**Stato Attività**")
        for label, icon in STATO_COLORS.items():
            st.markdown(f"{icon} {label}")
        st.markdown("---")

        st.markdown("**Colonne visibili**")
        changed = False
        for col in col_order:
            new_val = st.checkbox(col, value=prefs.get(col, True), key=f"pref_{page}_{col}")
            if new_val != prefs.get(col, True):
                prefs[col] = new_val
                changed = True
        if changed:
            save_prefs(prefs, page)

        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.resp_name = None
            st.switch_page("streamlit_app.py")

    return changed
