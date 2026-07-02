import streamlit as st

st.set_page_config(
    page_title="Gestione Progetti — Ennio Schiavoni",
    page_icon="📋",
    layout="wide",
)

if st.secrets.get("auth", {}).get("dev_mode", False):
    st.session_state.logged_in = True
    st.session_state.role = "owner"
    st.session_state.resp_name = "Ennio Schiavoni"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.resp_name = None

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("## 📋 Gestione Progetti 2026")
        st.markdown("---")
        role = st.radio("Accedi come", ["Owner (Ennio)", "Responsabile Progetto"], horizontal=True)
        password = st.text_input("Password", type="password")

        if role == "Responsabile Progetto":
            from utils.data import load_data
            df = load_data()
            resp_list = sorted(df["Resp.Progetto"].dropna().unique())
            resp_name = st.selectbox("Seleziona il tuo nome", resp_list)
        else:
            resp_name = "Ennio Schiavoni"

        if st.button("Accedi", use_container_width=True):
            secrets = st.secrets["auth"]
            if role == "Owner (Ennio)" and password == secrets["owner_password"]:
                st.session_state.logged_in = True
                st.session_state.role = "owner"
                st.session_state.resp_name = resp_name
                st.rerun()
            elif role == "Responsabile Progetto" and password == secrets["resp_password"]:
                st.session_state.logged_in = True
                st.session_state.role = "resp"
                st.session_state.resp_name = resp_name
                st.rerun()
            else:
                st.error("Password errata.")
else:
    st.switch_page("pages/1_Dashboard.py")
