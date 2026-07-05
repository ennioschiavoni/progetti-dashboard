import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data import load_data, TIPO_OPTIONS, STATO_OPTIONS, SORT_COLS
from utils.prefs import load_prefs, load_col_order
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Dashboard Progetti", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

if not st.session_state.get("logged_in"):
    st.warning("Accesso richiesto.")
    st.switch_page("streamlit_app.py")

role = st.session_state.role
resp_name = st.session_state.resp_name

if "col_prefs_dashboard" not in st.session_state:
    st.session_state.col_prefs_dashboard = load_prefs("dashboard")
if "col_order_dashboard" not in st.session_state:
    st.session_state.col_order_dashboard = load_col_order("dashboard")
if "dash_grid_v" not in st.session_state:
    st.session_state.dash_grid_v = 0
prefs = st.session_state.col_prefs_dashboard
col_order = st.session_state.col_order_dashboard

changed = render_sidebar(role, resp_name, prefs, col_order, page="dashboard")
if changed:
    st.session_state.col_prefs_dashboard = prefs

df = load_data()

# Filtri
def _reset_dash():
    for k in ["dash_f_cliente", "dash_f_resp", "dash_f_trpr", "dash_f_tipo"]:
        st.session_state[k] = []
    st.session_state.dash_sort_col = "Ordina per Cliente"
    st.session_state.dash_sort_dir = "Ordina A → Z"

fc1, fc2, fc3, fc4, _ = st.columns([2, 2, 2, 2, 4])
with fc1:
    clienti = sorted(df["Cliente"].dropna().unique().tolist())
    sel_cliente = st.multiselect("", clienti, placeholder="Filtra per Cliente", label_visibility="collapsed", key="dash_f_cliente")
with fc2:
    resps = sorted(df["Resp.Progetto"].dropna().unique().tolist())
    sel_resp = st.multiselect("", resps, placeholder="Filtra per Project Manager", label_visibility="collapsed", key="dash_f_resp")
with fc3:
    sel_trpr = st.multiselect("", ["TR", "PR"], placeholder="Filtra per TR / PR", label_visibility="collapsed", key="dash_f_trpr")
with fc4:
    _tipo_vals = sorted(df["Tipo Attività"].dropna().unique().tolist())
    sel_tipo = st.multiselect("", _tipo_vals + ["Escludi Presale Cliente"], placeholder="Filtra per Tipo Attività", label_visibility="collapsed", key="dash_f_tipo")

filtered = df.copy()
if sel_cliente:
    filtered = filtered[filtered["Cliente"].isin(sel_cliente)]
if sel_resp:
    filtered = filtered[filtered["Resp.Progetto"].isin(sel_resp)]
if sel_trpr:
    filtered = filtered[filtered["TR_PR"].isin(sel_trpr)]
if sel_tipo:
    if "Escludi Presale Cliente" in sel_tipo:
        filtered = filtered[filtered["Tipo Attività"] != "Presale Cliente"]
    else:
        filtered = filtered[filtered["Tipo Attività"].isin(sel_tipo)]
# Filtro rapido da home page (es. Stato Critico)
if st.session_state.pop("dash_quick_stato", None) == "Critica":
    filtered = filtered[filtered["Stato Attività"].str.contains("Critica", na=False)]


all_cols = ["Tipo_Icon", "Stato_Icon", "Tipo Attività", "Stato Attività", "Cliente", "Resp.Progetto", "Attività",
            "Stato_Resp", "Note Ennio", "Next Step COM",
            "TR_PR", "Data Rilascio", "Data SAL", "Project Manager", "Owner"]

display_df = filtered[all_cols].rename(columns={
    "Tipo_Icon":       "Tipo",
    "Stato_Icon":      "Stato",
    "Resp.Progetto":   "Project Manager",
    "Stato_Resp":      "Stato (PM)",
    "Next Step COM":   "Next Step",
    "TR_PR":           "TR/PR",
    "Data Rilascio":   "Rilascio",
    "Project Manager": "PM",
})

display_df["Data SAL"] = pd.to_datetime(display_df["Data SAL"], errors="coerce").dt.strftime("%-d/%m/%Y").fillna("")

# Applica ordine colonne salvato (Tipo e Stato sempre in testa)
ordered_cols = ["Tipo", "Stato"] + [c for c in col_order if c in display_df.columns]
display_df = display_df[ordered_cols]

if "dash_sort_col" not in st.session_state:
    st.session_state.dash_sort_col = "Ordina per Cliente"

sc1, sc2, sc_fit, sc_r, _ = st.columns([2, 2, 1, 1, 6], vertical_alignment="bottom")
with sc1:
    sort_by = st.selectbox("", list(SORT_COLS.keys()), index=None, placeholder="Ordina per", label_visibility="collapsed", key="dash_sort_col")
with sc2:
    sort_asc = st.selectbox("", ["Ordina A → Z", "Ordina Z → A"], label_visibility="collapsed", key="dash_sort_dir") == "Ordina A → Z"
with sc_fit:
    if st.button("⇔ Fit", key="dash_fit", use_container_width=True):
        st.session_state.dash_grid_v += 1
with sc_r:
    st.markdown('<div class="reset-marker" style="display:none"></div>', unsafe_allow_html=True)
    st.button("✕ Reset", key="dash_reset", on_click=_reset_dash, use_container_width=True)
if sel_resp:
    filtered = filtered.copy()
    filtered["_presale_last"] = filtered["Tipo Attività"].apply(
        lambda x: 1 if str(x).startswith("Presale") else 0)
    filtered = filtered.sort_values(["Cliente", "_presale_last"], ascending=[True, True], na_position="last")
    filtered = filtered.drop(columns=["_presale_last"])
elif sort_by and SORT_COLS.get(sort_by):
    filtered = filtered.sort_values(SORT_COLS[sort_by], ascending=sort_asc, na_position="last")

if sel_resp or (sort_by and SORT_COLS.get(sort_by)):
    display_df = filtered[all_cols].rename(columns={
        "Tipo_Icon": "Tipo", "Stato_Icon": "Stato",
        "Resp.Progetto": "Project Manager", "Stato_Resp": "Stato (PM)", "Next Step COM": "Next Step",
        "TR_PR": "TR/PR", "Data Rilascio": "Rilascio", "Project Manager": "PM", "Data SAL": "Data SAL",
    })
    display_df["Data SAL"] = pd.to_datetime(display_df["Data SAL"], errors="coerce").dt.strftime("%-d/%m/%Y").fillna("")
    ordered_cols = ["Tipo", "Stato"] + [c for c in col_order if c in display_df.columns]
    display_df = display_df[ordered_cols]

row_style = JsCode("""
function(params) {
    var tipo = params.data ? params.data['Tipo Attività'] : null;
    if (tipo === 'Presale Cliente' || tipo === 'Presale Prospect') {
        return { 'color': '#8B0000' };
    }
    if (tipo === 'Interna') {
        return { 'color': '#1565C0' };
    }
}
""")

auto_size_js  = JsCode("function(p){ p.api.autoSizeAllColumns(true); }")
cell_style_js = JsCode("""
function(params) {
    if (params.value && String(params.value).indexOf('?') !== -1) {
        return { 'backgroundColor': '#FFFF99' };
    }
}
""")

gb = GridOptionsBuilder.from_dataframe(display_df)
gb.configure_default_column(resizable=True, sortable=False, filter=False, wrapText=True, autoHeight=False,
                             suppressMenu=True)
gb.configure_grid_options(rowHeight=40, getRowStyle=row_style, onFirstDataRendered=auto_size_js)

col_defs = {
    "Tipo":           {"minWidth": 50, "maxWidth": 58, "cellStyle": {"textAlign": "center"}},
    "Stato":          {"minWidth": 52, "maxWidth": 60, "cellStyle": {"textAlign": "center"}},
    "Cliente":        {"flex": 3, "minWidth": 80,  "hide": not prefs["Cliente"]},
    "Attività":       {"flex": 6, "minWidth": 120, "hide": not prefs["Attività"]},
    "Tipo Attività":  {"flex": 5, "minWidth": 130, "hide": not prefs["Tipo Attività"]},
    "Stato Attività": {"flex": 6, "minWidth": 150, "hide": not prefs["Stato Attività"]},
    "Project Manager": {"flex": 4, "minWidth": 110, "hide": not prefs["Project Manager"]},
    "Stato (PM)":      {"flex": 7, "minWidth": 150, "hide": not prefs["Stato (PM)"], "cellStyle": cell_style_js},
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

grid_response = AgGrid(
    display_df,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.GRID_CHANGED,
    fit_columns_on_grid_load=False,
    height=2000,
    theme="streamlit",
    reload_data=True,
    key=f"aggrid_dashboard_{st.session_state.dash_grid_v}",
    allow_unsafe_jscode=True,
)

