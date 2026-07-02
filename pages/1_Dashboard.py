import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data import load_data, TIPO_OPTIONS, STATO_OPTIONS, SORT_COLS
from utils.prefs import load_prefs
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Dashboard Progetti", page_icon="📊", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("Accesso richiesto.")
    st.switch_page("streamlit_app.py")

role = st.session_state.role
resp_name = st.session_state.resp_name

if "col_prefs_dashboard" not in st.session_state:
    st.session_state.col_prefs_dashboard = load_prefs("dashboard")
prefs = st.session_state.col_prefs_dashboard

changed = render_sidebar(role, resp_name, prefs, page="dashboard")
if changed:
    st.session_state.col_prefs_dashboard = prefs

df = load_data()
if role == "resp":
    df = df[df["Resp.Progetto"] == resp_name]

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


all_cols = ["Tipo_Icon", "Stato_Icon", "Tipo Attività", "Stato Attività", "Cliente", "Resp.Progetto", "Attività",
            "Stato_Resp", "Note Ennio", "Next Step COM",
            "TR_PR", "Data Rilascio", "Data SAL", "Project Manager", "Owner"]

display_df = filtered[all_cols].rename(columns={
    "Tipo_Icon":       "Tipo",
    "Stato_Icon":      "Stato",
    "Resp.Progetto":   "Resp.",
    "Stato_Resp":      "Stato (Resp.)",
    "Next Step COM":   "Next Step",
    "TR_PR":           "TR/PR",
    "Data Rilascio":   "Rilascio",
    "Project Manager": "PM",
})

display_df["Data SAL"] = pd.to_datetime(display_df["Data SAL"], errors="coerce").dt.strftime("%-d/%m/%Y").fillna("")

sc1, sc2 = st.columns([3, 1])
with sc1:
    sort_by = st.selectbox("Ordina per", list(SORT_COLS.keys()), label_visibility="visible", key="dash_sort_col")
with sc2:
    sort_asc = st.selectbox("Ordine", ["↑ A→Z", "↓ Z→A"], label_visibility="visible", key="dash_sort_dir") == "↑ A→Z"
if SORT_COLS[sort_by]:
    filtered = filtered.sort_values(SORT_COLS[sort_by], ascending=sort_asc, na_position="last")
    display_df = filtered[all_cols].rename(columns={
        "Tipo_Icon": "Tipo", "Stato_Icon": "Stato",
        "Resp.Progetto": "Resp.", "Stato_Resp": "Stato (Resp.)", "Next Step COM": "Next Step",
        "TR_PR": "TR/PR", "Data Rilascio": "Rilascio", "Project Manager": "PM", "Data SAL": "Data SAL",
    })
    display_df["Data SAL"] = pd.to_datetime(display_df["Data SAL"], errors="coerce").dt.strftime("%-d/%m/%Y").fillna("")

row_style = JsCode("""
function(params) {
    var tipo = params.data ? params.data['Tipo Attività'] : null;
    if (tipo === 'Presale Cliente' || tipo === 'Presale Prospect') {
        return { 'color': '#8B0000' };
    }
}
""")

gb = GridOptionsBuilder.from_dataframe(display_df)
gb.configure_default_column(resizable=True, sortable=True, filter=True, wrapText=True, autoHeight=False)
menu_items = JsCode("function(p){ return ['autoSizeThis','autoSizeAll']; }")
gb.configure_grid_options(rowHeight=52, getRowStyle=row_style, getMainMenuItems=menu_items)

col_defs = {
    "Tipo":           {"flex": 1, "minWidth": 70, "maxWidth": 90},
    "Stato":          {"flex": 1, "minWidth": 70, "maxWidth": 90},
    "Cliente":        {"flex": 3, "minWidth": 80,  "hide": not prefs["Cliente"]},
    "Attività":       {"flex": 6, "minWidth": 120, "hide": not prefs["Attività"]},
    "Tipo Attività":  {"flex": 5, "minWidth": 130, "hide": not prefs["Tipo Attività"]},
    "Stato Attività": {"flex": 6, "minWidth": 150, "hide": not prefs["Stato Attività"]},
    "Resp.":          {"flex": 4, "minWidth": 110, "hide": not prefs["Resp."]},
    "Stato (Resp.)":  {"flex": 7, "minWidth": 150, "hide": not prefs["Stato (Resp.)"]},
    "Note Ennio":     {"flex": 7, "minWidth": 150, "hide": not prefs["Note Ennio"]},
    "Next Step":      {"flex": 5, "minWidth": 110, "hide": not prefs["Next Step"]},
    "TR/PR":          {"flex": 1, "minWidth": 50,  "hide": not prefs["TR/PR"], "maxWidth": 65},
    "Rilascio":       {"flex": 3, "minWidth": 80,  "hide": not prefs["Rilascio"]},
    "Data SAL":       {"flex": 3, "minWidth": 80,  "hide": not prefs["Data SAL"]},
    "PM":             {"flex": 4, "minWidth": 110, "hide": not prefs["PM"]},
    "Owner":          {"flex": 4, "minWidth": 110, "hide": not prefs["Owner"]},
}
for col, opts in col_defs.items():
    gb.configure_column(col, **opts)

AgGrid(
    display_df,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.NO_UPDATE,
    fit_columns_on_grid_load=True,
    height=2000,
    theme="streamlit",
    reload_data=True,
    key="aggrid_dashboard",
    allow_unsafe_jscode=True,
)
