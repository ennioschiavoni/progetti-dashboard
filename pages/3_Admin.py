import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data import load_data, save_data
from utils.excel_sync import excel_disponibile, excel_to_df, csv_to_excel, EXCEL_PATH

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

tab1, tab2, tab3 = st.tabs(["➕ Aggiungi Attività", "🗑️ Elimina Attività", "📊 Sync Excel"])

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

with tab3:
    st.markdown("### 📊 Sincronizzazione Excel ↔ App")

    if not excel_disponibile():
        st.info("Questa funzione è disponibile solo su localhost con Dropbox sincronizzato.")
        st.caption(f"Percorso atteso: `{EXCEL_PATH}`")
    else:
        st.caption(f"File: `{EXCEL_PATH.name}`")
        st.markdown("---")

        # ── Excel → CSV ───────────────────────────────────────────────────────
        st.markdown("#### 📥 Importa da Excel → App")
        st.warning(
            "**Attenzione:** sovrascrive tutti i dati dell'app con quelli dell'Excel. "
            "Le modifiche fatte solo nell'app (non presenti in Excel) andranno perse."
        )
        col1, col2 = st.columns([1, 3])
        with col1:
            preview_xls = st.button("👁 Anteprima", key="prev_xls")
        with col2:
            import_xls = st.button("📥 Importa da Excel", type="primary", key="imp_xls")

        if preview_xls:
            try:
                xls_df = excel_to_df()
                st.info(f"Excel: **{len(xls_df)} righe** — App attuale: **{len(df)} righe**")
                st.dataframe(xls_df.head(10), use_container_width=True)
            except Exception as e:
                st.error(f"Errore lettura Excel: {e}")

        if import_xls:
            try:
                xls_df = excel_to_df()
                save_data(xls_df)
                st.success(f"Importate {len(xls_df)} righe da Excel. App aggiornata.")
                st.rerun()
            except Exception as e:
                st.error(f"Errore importazione: {e}")

        st.markdown("---")

        # ── CSV → Excel ───────────────────────────────────────────────────────
        st.markdown("#### 📤 Sincronizza App → Excel")
        st.info(
            "Aggiorna le righe esistenti nell'Excel con i dati dell'app. "
            "Le righe nuove (aggiunte nell'app ma non in Excel) vengono aggiunte in fondo. "
            "La formattazione Excel è preservata."
        )
        if st.button("📤 Sincronizza verso Excel", type="primary", key="sync_xls"):
            try:
                updated, added = csv_to_excel(df)
                st.success(f"Excel aggiornato: **{updated} righe aggiornate**, **{added} righe aggiunte**.")
            except Exception as e:
                st.error(f"Errore sincronizzazione: {e}")
