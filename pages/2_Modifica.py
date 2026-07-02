import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data import load_data, save_data, TIPO_OPTIONS, STATO_OPTIONS, PM_EDITABLE_COLS, SORT_COLS
from utils.prefs import load_prefs
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Modifica Attività", page_icon="✏️", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("Accesso richiesto.")
    st.switch_page("streamlit_app.py")

role = st.session_state.role
resp_name = st.session_state.resp_name

if "col_prefs_modifica" not in st.session_state:
    st.session_state.col_prefs_modifica = load_prefs("modifica")
if "editor_v" not in st.session_state:
    st.session_state.editor_v = 0
if "dup_rows" not in st.session_state:
    st.session_state.dup_rows = []
prefs = st.session_state.col_prefs_modifica

changed = render_sidebar(role, resp_name, prefs, page="modifica")
if changed:
    st.session_state.col_prefs_modifica = prefs

df = load_data()
if role == "resp":
    df = df[df["Resp.Progetto"] == resp_name]

resp_vals = sorted(df["Resp.Progetto"].dropna().unique().tolist())

# Filtri
fc1, fc2, fc3, fc4, fc5 = st.columns(5)
LBL = '<p style="font-size:13px;margin:0 0 2px 0;font-weight:600">{}</p>'
with fc1:
    st.markdown(LBL.format("Cliente"), unsafe_allow_html=True)
    clienti = ["Tutti"] + sorted(df["Cliente"].dropna().unique().tolist())
    sel_cliente = st.selectbox("Cliente", clienti, label_visibility="collapsed")
with fc2:
    if role == "owner":
        st.markdown(LBL.format("Resp. Progetto"), unsafe_allow_html=True)
        resps = ["Tutti"] + sorted(df["Resp.Progetto"].dropna().unique().tolist())
        sel_resp = st.selectbox("Resp. Progetto", resps, label_visibility="collapsed")
    else:
        sel_resp = resp_name
with fc3:
    st.markdown(LBL.format("Tipo Attività"), unsafe_allow_html=True)
    tipo_vals = sorted(df["Tipo Attività"].replace("", None).dropna().unique().tolist())
    sel_tipo = st.selectbox("Tipo Attività", ["Tutti"] + tipo_vals, label_visibility="collapsed")
with fc4:
    st.markdown(LBL.format("Stato Attività"), unsafe_allow_html=True)
    stato_vals = sorted(df["Stato Attività"].replace("", None).dropna().unique().tolist())
    sel_stato = st.selectbox("Stato Attività", ["Tutti"] + stato_vals, label_visibility="collapsed")
with fc5:
    st.markdown(LBL.format("TR / PR"), unsafe_allow_html=True)
    sel_trpr = st.selectbox("TR / PR", ["Tutti", "TR", "PR"], label_visibility="collapsed")

filtered = df.copy()
if sel_cliente != "Tutti":
    filtered = filtered[filtered["Cliente"] == sel_cliente]
if role == "owner" and sel_resp != "Tutti":
    filtered = filtered[filtered["Resp.Progetto"] == sel_resp]
if sel_tipo != "Tutti":
    filtered = filtered[filtered["Tipo Attività"] == sel_tipo]
if sel_stato != "Tutti":
    filtered = filtered[filtered["Stato Attività"] == sel_stato]
if sel_trpr != "Tutti":
    filtered = filtered[filtered["TR_PR"] == sel_trpr]

filtered = filtered.copy()
filtered["_idx"] = filtered.index

sc1, sc2, sc3, sc4, sc5 = st.columns([2, 1, 3, 1, 1])
with sc1:
    sort_by = st.selectbox("Ordina per", list(SORT_COLS.keys()), label_visibility="visible", key="sort_col")
with sc2:
    sort_asc = st.selectbox("Ordine", ["↑ A→Z", "↓ Z→A"], label_visibility="visible", key="sort_dir") == "↑ A→Z"
with sc3:
    dup_options = ["—"] + [f"{r['Cliente']}  |  {r['Attività']}" for _, r in filtered.iterrows()]
    dup_sel = st.selectbox("Duplica riga", dup_options, label_visibility="visible", key="dup_sel")
with sc4:
    st.markdown("&nbsp;", unsafe_allow_html=True)
    dup_clicked = st.button("📋 Duplica", use_container_width=True)
with sc5:
    st.markdown("&nbsp;", unsafe_allow_html=True)
    save_clicked = st.button("💾 Salva", type="primary", use_container_width=True)

if dup_clicked and dup_sel != "—":
    dup_idx = dup_options.index(dup_sel) - 1
    dup_row = filtered.iloc[dup_idx].copy()
    dup_row["Attività"] = "COPIA - " + str(dup_row["Attività"])
    dup_row["_idx"] = -1
    st.session_state.dup_rows.append(dup_row.to_dict())
    st.session_state.editor_v += 1
    st.rerun()

if SORT_COLS[sort_by]:
    filtered = filtered.sort_values(SORT_COLS[sort_by], ascending=sort_asc, na_position="last")

# ── Tabella editabile ────────────────────────────────────────────────────────
owner_editable = {"Cliente", "Attività", "Tipo Attività", "Stato Attività",
                  "Resp.Progetto", "Stato_Resp", "Note Ennio", "Next Step COM",
                  "TR_PR", "Data Rilascio", "Project Manager", "Owner"}
pm_editable    = {"Tipo Attività", "Stato Attività", "Stato_Resp", "Note Ennio", "Next Step COM"}
editable_cols  = owner_editable if role == "owner" else pm_editable

display_cols = ["Tipo_Icon", "Stato_Icon", "Tipo Attività", "Stato Attività", "Cliente", "Resp.Progetto", "Attività",
                "Stato_Resp", "Note Ennio", "Next Step COM",
                "TR_PR", "Data Rilascio", "Data SAL", "Project Manager", "Owner", "_idx"]

work = filtered[display_cols].copy()
for col in ["Tipo Attività", "Stato Attività", "Resp.Progetto", "TR_PR",
            "Stato_Resp", "Note Ennio", "Next Step COM"]:
    if col in work.columns:
        work[col] = work[col].fillna("").astype(str).replace("nan", "")
work["Data SAL"] = pd.to_datetime(work["Data SAL"], errors="coerce").dt.strftime("%-d/%m/%Y").fillna("")

if st.session_state.dup_rows:
    dup_df = pd.DataFrame(st.session_state.dup_rows)[display_cols]
    work = pd.concat([work, dup_df], ignore_index=True)

# Valori fuori dalle opzioni → svuota cella così risulta editabile
work["Tipo Attività"] = work["Tipo Attività"].apply(
    lambda v: v if v in TIPO_OPTIONS else "")
work["Stato Attività"] = work["Stato Attività"].apply(
    lambda v: v if v in STATO_OPTIONS else "")

disabled_cols = ["Tipo_Icon", "Stato_Icon", "_idx"] + [
    c for c in display_cols if c not in editable_cols
]

# Colonne visibili in base ai checkbox della sidebar
PREFS_TO_COL = {
    "Cliente":        "Cliente",
    "Attività":       "Attività",
    "Tipo Attività":  "Tipo Attività",
    "Stato Attività": "Stato Attività",
    "Resp.":          "Resp.Progetto",
    "Stato (Resp.)":  "Stato_Resp",
    "Note Ennio":     "Note Ennio",
    "Next Step":      "Next Step COM",
    "TR/PR":          "TR_PR",
    "Rilascio":       "Data Rilascio",
    "Data SAL":       "Data SAL",
    "PM":             "Project Manager",
    "Owner":          "Owner",
}
col_order = ["Tipo_Icon", "Stato_Icon"] + [
    PREFS_TO_COL[k] for k in PREFS_TO_COL if prefs.get(k, True)
]

n_rows = len(work)
grid_h = max(400, n_rows * 35 + 50)

edited = st.data_editor(
    work,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    disabled=disabled_cols,
    height=grid_h,
    column_order=col_order,
    key=f"mod_editor_{st.session_state.editor_v}",
    column_config={
        "Tipo_Icon":       st.column_config.TextColumn("Tipo", width=55),
        "Stato_Icon":      st.column_config.TextColumn("Stato", width=55),
        "Cliente":         st.column_config.TextColumn("Cliente", width=90),
        "Attività":        st.column_config.TextColumn("Attività", width=170),
        "Tipo Attività":   st.column_config.SelectboxColumn(
                               "Tipo Attività", width=155,
                               options=TIPO_OPTIONS, required=False),
        "Stato Attività":  st.column_config.SelectboxColumn(
                               "Stato Attività", width=180,
                               options=STATO_OPTIONS, required=False),
        "Resp.Progetto":   st.column_config.SelectboxColumn(
                               "Resp.", width=135,
                               options=resp_vals, required=False),
        "Stato_Resp":      st.column_config.TextColumn("Stato (Resp.)", width=210),
        "Note Ennio":      st.column_config.TextColumn("Note Ennio", width=210),
        "Next Step COM":   st.column_config.TextColumn("Next Step", width=150),
        "TR_PR":           st.column_config.TextColumn("TR/PR", width=60),
        "Data Rilascio":   st.column_config.TextColumn("Rilascio", width=90),
        "Data SAL":        st.column_config.TextColumn("Data SAL", width=90),
        "Project Manager": st.column_config.TextColumn("PM", width=130),
        "Owner":           st.column_config.TextColumn("Owner", width=130),
        "_idx":            None,
    }
)

if save_clicked:
    other        = df.drop(filtered["_idx"].tolist()).copy()
    edited_clean = edited.drop(columns=["Tipo_Icon", "Stato_Icon", "_idx"], errors="ignore")
    merged       = pd.concat([other, edited_clean], ignore_index=True)
    save_data(merged)
    st.session_state.editor_v += 1
    st.session_state.dup_rows = []
    st.success("Salvato!")
    st.rerun()
