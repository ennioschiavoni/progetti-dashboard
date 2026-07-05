import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data import load_data, save_data

st.set_page_config(page_title="Amministrazione", page_icon="⚙️", layout="wide")

if not st.session_state.get("logged_in"):
    st.switch_page("streamlit_app.py")

if st.session_state.role != "owner":
    st.error("Sezione riservata all'Owner.")
    st.stop()

resp_name = st.session_state.resp_name

with st.sidebar:
    st.markdown(f"👤 **{resp_name}**")
    st.markdown("Ruolo: Owner")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.resp_name = None
        st.switch_page("streamlit_app.py")

df = load_data()

st.markdown("## ⚙️ Amministrazione")
st.markdown("---")

tab1, tab2 = st.tabs(["➕ Aggiungi Attività", "🗑️ Elimina Attività"])

with tab1:
    st.markdown("### Nuova Attività")
    resps = sorted(df["Resp.Progetto"].dropna().unique().tolist())
    clienti = sorted(df["Cliente"].dropna().unique().tolist())

    c1, c2 = st.columns(2)
    with c1:
        new_cliente = st.selectbox("Cliente", ["— nuovo —"] + clienti, key="nc")
        if new_cliente == "— nuovo —":
            new_cliente = st.text_input("Nome cliente", key="nc2")
        new_attivita = st.text_input("Attività")
        new_resp = st.selectbox("Project Manager", resps, key="nr")
    with c2:
        new_stato = st.text_area("Stato", height=80)
        new_note = st.text_area("Note Ennio", height=80)
        new_next = st.text_input("Next Step COM")
        new_trpr = st.selectbox("TR/PR", ["", "TR", "PR"])
        new_pm = st.text_input("Project Manager")
        new_owner = st.text_input("Owner")

    if st.button("➕ Aggiungi", type="primary"):
        if new_attivita and new_cliente:
            new_row = {
                "Cliente": new_cliente,
                "Attività": new_attivita,
                "Resp.Progetto": new_resp,
                "Stato": new_stato,
                "Note Ennio": new_note,
                "Next Step COM": new_next,
                "TR_PR": new_trpr,
                "Data Rilascio": None,
                "Data SAL": None,
                "Project Manager": new_pm,
                "Owner": new_owner,
                "Stato_Icon": "⚪",
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"Attività '{new_attivita}' aggiunta!")
            st.rerun()
        else:
            st.warning("Inserisci almeno Cliente e Attività.")

with tab2:
    st.markdown("### Elimina Attività")
    st.warning("Questa operazione è irreversibile.")

    sel_cliente = st.selectbox("Cliente", sorted(df["Cliente"].dropna().unique()), key="del_c")
    cliente_df = df[df["Cliente"] == sel_cliente]

    sel_att = st.selectbox("Attività", cliente_df["Attività"].tolist(), key="del_a")

    if st.button("🗑️ Elimina", type="primary"):
        idx = df[(df["Cliente"] == sel_cliente) & (df["Attività"] == sel_att)].index
        df = df.drop(idx).reset_index(drop=True)
        save_data(df)
        st.success("Attività eliminata.")
        st.rerun()
