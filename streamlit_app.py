import streamlit as st

st.set_page_config(
    page_title="Gestione Progetti — Websolute",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.secrets import get_auth as _get_auth
if _get_auth().get("dev_mode", False):
    st.session_state.logged_in = True
    st.session_state.role = "owner"
    st.session_state.resp_name = "Ennio Schiavoni"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.resp_name = None

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Forza light mode — fix dark system theme */
html { color-scheme: light !important; }
* { font-family: 'Inter', -apple-system, sans-serif !important; color: inherit; }

/* Sfondo bianco */
.stApp, .stApp > div, [data-testid="stAppViewContainer"] {
    background-color: #FFFFFF !important;
}
[data-testid="stHeader"] { background-color: #FFFFFF !important; }

.block-container {
    padding-top: 48px !important;
    padding-bottom: 24px !important;
    max-width: 1200px !important;
}

/* ── Card bianche ─────────────────────────────────────────────── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border-radius: 16px !important;
    border: none !important;
    box-shadow: 0 4px 24px rgba(15, 60, 120, 0.12) !important;
    padding: 1.4rem 1.6rem 1.4rem 1.6rem !important;
    height: 380px !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}

/* Barra colorata in cima */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.mk-login)   { box-shadow: 0 12px 48px rgba(15,60,120,0.18), inset 0 5px 0 #1E90FF !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.mk-global)  { box-shadow: 0 12px 48px rgba(15,60,120,0.18), inset 0 5px 0 #1E90FF !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.mk-resp)    { box-shadow: 0 12px 48px rgba(15,60,120,0.18), inset 0 5px 0 #8B5CF6 !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.mk-trpr)    { box-shadow: 0 12px 48px rgba(15,60,120,0.18), inset 0 5px 0 #F59E0B !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.mk-cliente) { box-shadow: 0 12px 48px rgba(15,60,120,0.18), inset 0 5px 0 #10B981 !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.mk-critico) { box-shadow: 0 12px 48px rgba(15,60,120,0.18), inset 0 5px 0 #EF4444 !important; }

/* Testo dentro le card: forza dark */
div[data-testid="stVerticalBlockBorderWrapper"] h3 { color: #111111 !important; font-size: 13px !important; font-weight: 700 !important; margin: 0 !important; }
div[data-testid="stVerticalBlockBorderWrapper"] p  { color: #555555 !important; font-size: 13px !important; line-height: 1.55 !important; margin: 0 !important; }
.card-title {
    font-size: 16px !important; font-weight: 700 !important; color: #111111 !important;
    white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important;
    min-width: 0 !important; flex: 1 !important; line-height: 1.2 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] label { color: #444444 !important; }
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] p { color: #555555 !important; font-size: 13px !important; }
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] p,
div[data-testid="stVerticalBlockBorderWrapper"] label p {
    color: #777777 !important; font-size: 11px !important;
    font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important;
}

/* Header card: icona a sx, titolo a dx */
.card-header {
    display: flex; align-items: center;
    gap: 10px; margin-bottom: 8px;
}
.card-header h3 { margin: 0 !important; }
.card-icon {
    width: 34px; height: 34px; border-radius: 8px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center; font-size: 17px;
}
.card-desc { color: #888888 !important; font-size: 12px; margin: 0 0 12px 0; line-height: 1.5; }

/* Stessa altezza card nella riga */
[data-testid="stHorizontalBlock"] { align-items: stretch !important; display: flex !important; }
[data-testid="stColumn"] { display: flex !important; flex-direction: column !important; }
[data-testid="stColumn"] > div { flex: 1 !important; display: flex !important; flex-direction: column !important; min-height: 0 !important; }
[data-testid="stColumn"] [data-testid="stVerticalBlock"] { flex: 1 !important; display: flex !important; flex-direction: column !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { flex: 1 !important; display: flex !important; flex-direction: column !important; box-sizing: border-box !important; }

/* Radio */
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label {
    background: #F5F5F5 !important; border: 1.5px solid #E8E8E8 !important;
    border-radius: 9px !important; padding: 7px 14px !important;
    font-size: 14px !important; font-weight: 500 !important; color: #222222 !important;
}

/* Input text/password */
div[data-testid="stVerticalBlockBorderWrapper"] input {
    background: #F7F7F7 !important; border: 1.5px solid #E5E5E5 !important;
    border-radius: 10px !important; height: 42px !important;
    font-size: 14px !important; color: #111111 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] input:focus {
    border-color: #3BA3F5 !important;
    box-shadow: 0 0 0 3px rgba(59,163,245,0.2) !important;
    background: #FFFFFF !important;
}

/* Selectbox & datalist autocomplete */
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSelectbox"] > div > div,
div[data-testid="stVerticalBlockBorderWrapper"] [data-baseweb="select"] {
    background: #F7F7F7 !important; border: 1.5px solid #E5E5E5 !important;
    border-radius: 10px !important; font-size: 14px !important; color: #111111 !important;
}

/* Bottoni primari — celeste Websolute (selettore corretto per Streamlit 1.50) */
[data-testid="stBaseButton"][kind="primary"],
button[kind="primary"] {
    border: none !important; border-radius: 11px !important; height: 46px !important;
    font-size: 14px !important; font-weight: 600 !important; color: #FFFFFF !important;
    background: #3BA3F5 !important; box-shadow: 0 4px 16px rgba(59,163,245,0.35) !important;
}
[data-testid="stBaseButton"][kind="primary"]:hover,
button[kind="primary"]:hover {
    background: #2291e8 !important;
    box-shadow: 0 6px 20px rgba(59,163,245,0.45) !important;
}

/* Logout / bottoni secondari */
[data-testid="stBaseButton"][kind="secondary"],
button[kind="secondary"] {
    border-radius: 10px !important; height: 40px !important; font-size: 14px !important;
    border: 1.5px solid #E0E0E0 !important; color: #555555 !important; background: transparent !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stAlert"] { border-radius: 9px !important; }

.locked-msg { color: #BBBBBB !important; font-size: 13px !important; font-style: italic; margin-top: 12px; }

/* Inner div della card: colonna flex per spingere bottone in fondo */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stButton"] {
    margin-top: auto !important;
}

/* Spaziatura griglia */
[data-testid="stHorizontalBlock"] { gap: 0.9rem !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0.9rem !important; }

/* Nasconde deploy button header */
[data-testid="stToolbar"] { display: none !important; }

/* Nasconde sidebar e toggle sulla homepage */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Logo ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:24px;">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:3px;">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="14" cy="14" r="14" fill="#3BA3F5"/>
            <text x="14" y="19" text-anchor="middle" font-family="Inter,sans-serif" font-size="14" font-weight="700" fill="white">w</text>
        </svg>
        <span style="color:#111111;font-size:22px;font-weight:300;letter-spacing:-0.3px;">websolute</span>
    </div>
    <p style="margin:0 0 0 38px;font-size:9px;color:#9AAAC0;font-weight:600;letter-spacing:2.5px;text-transform:uppercase;">Gestione Progetti 2026</p>
</div>
""", unsafe_allow_html=True)

# ── Dati ─────────────────────────────────────────────────────────────────────
logged_in = st.session_state.logged_in
role      = st.session_state.role

if logged_in:
    from utils.data import load_data
    _df          = load_data()
    clienti_list = sorted([c for c in _df["Cliente"].dropna().unique() if str(c).strip()])
    resp_list    = sorted([r for r in _df["Resp.Progetto"].dropna().unique() if str(r).strip()])
else:
    clienti_list, resp_list, clienti_opts, resp_opts = [], [], "", ""

# ── Riga 1: Login | Vista globale | Vedi Responsabile ─────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        st.markdown("""
        <div class="card-header mk-login">
            <div class="card-icon" style="background:#EBF5FF;">🔐</div>
            <span class="card-title">Login</span>
        </div>
        """, unsafe_allow_html=True)
        if not logged_in:
            usr = st.text_input("Utente", placeholder="Username", label_visibility="collapsed")
            pwd = st.text_input("Password", type="password", placeholder="••••••••",
                                label_visibility="collapsed")
            if st.button("Accedi →", use_container_width=True, type="primary", key="btn_login"):
                sec = _get_auth()
                if usr == sec["owner_username"] and pwd == sec["owner_password"]:
                    st.session_state.update(logged_in=True, role="owner", resp_name="Ennio Schiavoni")
                    st.rerun()
                elif usr == sec["resp_username"] and pwd == sec["resp_password"]:
                    st.session_state.update(logged_in=True, role="resp", resp_name="PM")
                    st.rerun()
                else:
                    st.error("Credenziali non valide.")
        else:
            st.success(f"✓ {st.session_state.resp_name}")
            if st.button("Logout", use_container_width=True, key="btn_logout"):
                st.session_state.update(logged_in=False, role=None, resp_name=None)
                st.rerun()

with c2:
    with st.container(border=True):
        st.markdown("""
        <div class="card-header mk-global">
            <div class="card-icon" style="background:#EBF5FF;">📊</div>
            <span class="card-title">Vista globale</span>
        </div>
        """, unsafe_allow_html=True)
        if logged_in:
            if st.button("Vai alla Dashboard →", use_container_width=True, type="primary", key="btn_global"):
                for k in ["dash_f_cliente", "dash_f_resp", "dash_f_trpr"]:
                    st.session_state[k] = []
                st.switch_page("pages/1_Dashboard.py")
        else:
            st.markdown('<p class="locked-msg">🔒 Accedi per continuare</p>', unsafe_allow_html=True)

with c3:
    with st.container(border=True):
        st.markdown("""
        <div class="card-header mk-resp">
            <div class="card-icon" style="background:#F3EEFF;">👤</div>
            <span class="card-title">Project Manager</span>
        </div>
        """, unsafe_allow_html=True)
        if logged_in and role == "owner":
            resp_sel = st.selectbox("", resp_list, index=None, placeholder="Cerca PM…",
                                    key="home_resp", label_visibility="collapsed")
            if st.button("Vai →", use_container_width=True, type="primary", key="btn_resp"):
                f = [resp_sel] if resp_sel else []
                st.session_state.update(**{"dash_f_resp": f, "dash_f_cliente": [], "dash_f_trpr": []})
                st.switch_page("pages/1_Dashboard.py")
        elif logged_in:
            st.markdown('<p class="locked-msg">Solo per gli Owner</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="locked-msg">🔒 Accedi per continuare</p>', unsafe_allow_html=True)

# ── Riga 2: PR/TR | Cliente | Stato Critico ───────────────────────────────────
c4, c5, c6 = st.columns(3)

with c4:
    with st.container(border=True):
        st.markdown("""
        <div class="card-header mk-trpr">
            <div class="card-icon" style="background:#FFF8E6;">📋</div>
            <span class="card-title">Preventivi / Trattative</span>
        </div>
        """, unsafe_allow_html=True)
        if logged_in:
            trpr_sel = st.selectbox("", ["Entrambi", "TR — Trattative", "PR — Preventivi"],
                                    key="home_trpr", label_visibility="collapsed")
            if st.button("Vai →", use_container_width=True, type="primary", key="btn_trpr"):
                mp = {"TR — Trattative": ["TR"], "PR — Preventivi": ["PR"], "Entrambi": ["TR", "PR"]}
                st.session_state.update(**{"dash_f_trpr": mp[trpr_sel], "dash_f_cliente": [], "dash_f_resp": []})
                st.switch_page("pages/1_Dashboard.py")
        else:
            st.markdown('<p class="locked-msg">🔒 Accedi per continuare</p>', unsafe_allow_html=True)

with c5:
    with st.container(border=True):
        st.markdown("""
        <div class="card-header mk-cliente">
            <div class="card-icon" style="background:#E6FAF4;">🏢</div>
            <span class="card-title">Vedi Cliente</span>
        </div>
        """, unsafe_allow_html=True)
        if logged_in:
            cliente_sel = st.selectbox("", clienti_list, index=None, placeholder="Cerca cliente…",
                                       key="home_cliente", label_visibility="collapsed")
            if st.button("Vai →", use_container_width=True, type="primary", key="btn_cliente"):
                f = [cliente_sel] if cliente_sel else []
                st.session_state.update(**{"dash_f_cliente": f, "dash_f_resp": [], "dash_f_trpr": []})
                st.switch_page("pages/1_Dashboard.py")
        else:
            st.markdown('<p class="locked-msg">🔒 Accedi per continuare</p>', unsafe_allow_html=True)

with c6:
    with st.container(border=True):
        st.markdown("""
        <div class="card-header mk-critico">
            <div class="card-icon" style="background:#FEF0F0;">🚨</div>
            <span class="card-title">Stato Critico</span>
        </div>
        """, unsafe_allow_html=True)
        if logged_in:
            if st.button("Vai →", use_container_width=True, type="primary", key="btn_critico"):
                st.session_state.update(**{"dash_f_cliente": [], "dash_f_resp": [], "dash_f_trpr": [],
                                           "dash_quick_stato": "Critica"})
                st.switch_page("pages/1_Dashboard.py")
        else:
            st.markdown('<p class="locked-msg">🔒 Accedi per continuare</p>', unsafe_allow_html=True)

