import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data import load_data, save_data, TIPO_OPTIONS, STATO_OPTIONS, SORT_COLS, TIPO_COLORS, STATO_COLORS
from utils.prefs import load_prefs, load_col_order
from utils.sidebar import render_sidebar

st.set_page_config(page_title="Modifica Attività", page_icon="✏️", layout="wide", initial_sidebar_state="expanded")

if not st.session_state.get("logged_in"):
    st.warning("Accesso richiesto.")
    st.switch_page("streamlit_app.py")

if st.session_state.get("role") != "owner":
    st.switch_page("pages/1_Dashboard.py")

import os
if not os.path.exists(".streamlit/secrets.toml"):
    st.info("✏️ La pagina Modifica è disponibile solo in locale (localhost:8502).\n\nPer modificare i dati, apri l'app sul tuo Mac.")
    st.stop()

role      = st.session_state.role
resp_name = st.session_state.resp_name

if "col_prefs_modifica" not in st.session_state:
    st.session_state.col_prefs_modifica = load_prefs("modifica")
if "col_order_modifica" not in st.session_state:
    st.session_state.col_order_modifica = load_col_order("modifica")
if "editor_v" not in st.session_state:
    st.session_state.editor_v = 0
if "work_override" not in st.session_state:
    st.session_state.work_override = None
if "sel_info" not in st.session_state:
    st.session_state.sel_info = None
if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

prefs     = st.session_state.col_prefs_modifica
col_order = st.session_state.col_order_modifica

changed = render_sidebar(role, resp_name, prefs, col_order, page="modifica")
if changed:
    st.session_state.col_prefs_modifica = prefs

df = load_data()
if role == "resp":
    df = df[df["Resp.Progetto"] == resp_name]

# ── Filtri ────────────────────────────────────────────────────────────────────
def _reset_mod():
    for k in ["mod_f_cliente", "mod_f_resp", "mod_f_trpr", "mod_f_tipo"]:
        st.session_state[k] = []
    st.session_state.sort_col = "Ordina per Cliente"
    st.session_state.sort_dir = "Ordina A → Z"
    st.session_state.sel_info = None

fc1, fc2, fc3, fc4, _ = st.columns([2, 2, 2, 2, 4])
with fc1:
    clienti     = sorted(df["Cliente"].dropna().unique().tolist())
    sel_cliente = st.multiselect("", clienti, placeholder="Filtra per Cliente",
                                 label_visibility="collapsed", key="mod_f_cliente")
with fc2:
    if role == "owner":
        resps    = sorted(df["Resp.Progetto"].dropna().unique().tolist())
        sel_resp = st.multiselect("", resps, placeholder="Filtra per Project Manager",
                                  label_visibility="collapsed", key="mod_f_resp")
    else:
        sel_resp = []
with fc3:
    sel_trpr = st.multiselect("", ["TR", "PR"], placeholder="Filtra per TR / PR",
                               label_visibility="collapsed", key="mod_f_trpr")
with fc4:
    _tipo_vals = sorted(df["Tipo Attività"].dropna().unique().tolist())
    sel_tipo = st.multiselect("", _tipo_vals + ["Escludi Presale Cliente"],
                               placeholder="Filtra per Tipo Attività",
                               label_visibility="collapsed", key="mod_f_tipo")

filtered = df.copy()
if sel_cliente:
    filtered = filtered[filtered["Cliente"].isin(sel_cliente)]
if role == "owner" and sel_resp:
    filtered = filtered[filtered["Resp.Progetto"].isin(sel_resp)]
if sel_trpr:
    filtered = filtered[filtered["TR_PR"].isin(sel_trpr)]
if sel_tipo:
    if "Escludi Presale Cliente" in sel_tipo:
        filtered = filtered[filtered["Tipo Attività"] != "Presale Cliente"]
    else:
        filtered = filtered[filtered["Tipo Attività"].isin(sel_tipo)]

filtered_index = filtered.index.tolist()

# ── Ordina ────────────────────────────────────────────────────────────────────
if "sort_col" not in st.session_state:
    st.session_state.sort_col = "Ordina per Cliente"

sc1, sc2, sc_save, sc_fit, sc_reset, _ = st.columns([2, 2, 1, 1, 1, 5], vertical_alignment="bottom")
with sc1:
    sort_by  = st.selectbox("", list(SORT_COLS.keys()), index=None,
                             placeholder="Ordina per",
                             label_visibility="collapsed", key="sort_col")
with sc2:
    sort_asc = st.selectbox("", ["Ordina A → Z", "Ordina Z → A"],
                             label_visibility="collapsed", key="sort_dir") == "Ordina A → Z"
with sc_save:
    save_clicked = st.button("💾 Salva", type="primary", use_container_width=True)
with sc_fit:
    if st.button("⇔ Fit", key="mod_fit", use_container_width=True):
        st.session_state.editor_v += 1
with sc_reset:
    st.markdown('<div class="reset-marker" style="display:none"></div>', unsafe_allow_html=True)
    st.button("✕ Reset", key="mod_reset", on_click=_reset_mod, use_container_width=True)

if sel_resp:
    filtered = filtered.copy()
    filtered["_pl"] = filtered["Tipo Attività"].apply(
        lambda x: 1 if str(x).startswith("Presale") else 0)
    filtered = filtered.sort_values(["Cliente", "_pl"], ascending=[True, True], na_position="last")
    filtered = filtered.drop(columns=["_pl"])
elif sort_by and SORT_COLS.get(sort_by):
    filtered = filtered.sort_values(SORT_COLS[sort_by], ascending=sort_asc, na_position="last")

# Invalida quando filtro o ordinamento cambiano → forza reset AgGrid
_fskey = (tuple(sorted(sel_cliente or [])), tuple(sorted(sel_resp or [])),
          tuple(sorted(sel_trpr)), tuple(sorted(sel_tipo)), sort_by, sort_asc)
if st.session_state.get("_filter_key") != _fskey:
    st.session_state._filter_key  = _fskey
    st.session_state.work_override = None
    st.session_state.sel_info      = None
    st.session_state.editor_v     += 1

# ── Barra azioni (sopra la griglia) ──────────────────────────────────────────
sel_info = st.session_state.sel_info
if sel_info:
    st.caption(f"**{sel_info['label']}**")
    a1, a2, a3, a4, _ = st.columns([2, 2, 2, 2, 4])
    with a1:
        if st.button("📋 Duplica sopra", use_container_width=True, key="act_dup_above"):
            st.session_state.pending_action = "dup_above"
    with a2:
        if st.button("📋 Duplica sotto", use_container_width=True, key="act_dup_below"):
            st.session_state.pending_action = "dup_below"
    with a3:
        if st.button("➕ Riga vuota dopo", use_container_width=True, key="act_ins"):
            st.session_state.pending_action = "insert"
    with a4:
        if st.button("🗑️ Elimina riga", use_container_width=True, key="act_del"):
            st.session_state.pending_action = "delete"

# ── Costruzione work ──────────────────────────────────────────────────────────
owner_editable = {"Cliente", "Attività", "Tipo Attività", "Stato Attività",
                  "Resp.Progetto", "Stato_Resp", "Note Ennio", "Next Step COM",
                  "TR_PR", "Data Rilascio", "Project Manager", "Owner"}
pm_editable    = {"Tipo Attività", "Stato Attività", "Stato_Resp", "Note Ennio", "Next Step COM"}
editable_cols  = owner_editable if role == "owner" else pm_editable

display_cols = ["Tipo_Icon", "Stato_Icon",
                "Stato Attività", "Tipo Attività", "Cliente", "Resp.Progetto",
                "Attività", "Stato_Resp", "Note Ennio", "Next Step COM",
                "TR_PR", "Data Rilascio", "Data SAL", "Project Manager", "Owner"]

if st.session_state.work_override is not None:
    work = st.session_state.work_override.copy()
    st.session_state.work_override = None
    # Ricalcola icone nel caso Tipo/Stato siano stati modificati
    work["Tipo_Icon"]  = work["Tipo Attività"].map(TIPO_COLORS).fillna("⚪")
    work["Stato_Icon"] = work["Stato Attività"].map(STATO_COLORS).fillna("⚪")
else:
    work = filtered[display_cols].copy().reset_index(drop=True)
    for col in ["Tipo Attività", "Stato Attività", "Resp.Progetto", "TR_PR",
                "Stato_Resp", "Note Ennio", "Next Step COM"]:
        if col in work.columns:
            work[col] = work[col].fillna("").astype(str).replace("nan", "")
    work["Data SAL"] = (pd.to_datetime(work["Data SAL"], errors="coerce")
                        .dt.strftime("%-d/%m/%Y").fillna(""))

work["_row_idx"] = range(len(work))
if "_check" not in work.columns:
    work.insert(0, "_check", "")

# ── AgGrid ───────────────────────────────────────────────────────────────────
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

gb = GridOptionsBuilder.from_dataframe(work)
gb.configure_default_column(resizable=True, sortable=False, filter=False,
                             wrapText=True, autoHeight=False, suppressMenu=True)
gb.configure_selection("single", use_checkbox=False,
                        pre_selected_rows=[sel_info["pos"]] if sel_info else [])
gb.configure_grid_options(rowHeight=28, getRowStyle=row_style, onFirstDataRendered=auto_size_js)

gb.configure_column("_check",    headerName="✏️", width=45, maxWidth=45, minWidth=45,
                    checkboxSelection=True, editable=False, resizable=False)
gb.configure_column("_row_idx",  hide=True)
gb.configure_column("Tipo_Icon",  headerName="Tipo",  minWidth=50, maxWidth=58, editable=False,
                    cellStyle={"textAlign": "center"})
gb.configure_column("Stato_Icon", headerName="Stato", minWidth=52, maxWidth=60, editable=False,
                    cellStyle={"textAlign": "center"})

PREF_TO_FIELD = {
    "Stato Attività":  "Stato Attività",
    "Tipo Attività":   "Tipo Attività",
    "Cliente":         "Cliente",
    "Project Manager": "Resp.Progetto",
    "Attività":        "Attività",
    "Stato (PM)":      "Stato_Resp",
    "Note Ennio":      "Note Ennio",
    "Next Step":       "Next Step COM",
    "TR/PR":           "TR_PR",
    "Rilascio":        "Data Rilascio",
    "Data SAL":        "Data SAL",
    "PM":              "Project Manager",
    "Owner":           "Owner",
}
hidden_fields = {PREF_TO_FIELD[k] for k, v in prefs.items() if not v and k in PREF_TO_FIELD}

col_defs = [
    ("Stato Attività",  "Stato Attività",  180, dict(cellEditor="agSelectCellEditor",
                                                      cellEditorParams={"values": STATO_OPTIONS},
                                                      cellEditorPopup=True)),
    ("Tipo Attività",   "Tipo Attività",   155, dict(cellEditor="agSelectCellEditor",
                                                      cellEditorParams={"values": TIPO_OPTIONS},
                                                      cellEditorPopup=True)),
    ("Cliente",         "Cliente",          90, {}),
    ("Resp.Progetto",   "Project Manager", 135, {}),
    ("Attività",        "Attività",        170, {}),
    ("Stato_Resp",      "Stato (PM)",      210, {"cellStyle": cell_style_js}),
    ("Note Ennio",      "Note Ennio",      210, {}),
    ("Next Step COM",   "Next Step",       150, {}),
    ("TR_PR",           "TR/PR",            60, {}),
    ("Data Rilascio",   "Rilascio",         90, {}),
    ("Data SAL",        "Data SAL",         90, {}),
    ("Project Manager", "PM",              130, {}),
    ("Owner",           "Owner",           130, {}),
]
for field, header, width, extra in col_defs:
    gb.configure_column(field, headerName=header, width=width,
                        editable=field in editable_cols,
                        hide=field in hidden_fields,
                        **extra)

grid_response = AgGrid(
    work,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=False,
    height=1000,
    theme="streamlit",
    reload_data=False,
    key=f"mod_aggrid_{st.session_state.editor_v}",
    allow_unsafe_jscode=True,
)

# ── Aggiorna sel_info ─────────────────────────────────────────────────────────
sel_rows = grid_response.selected_rows
has_sel  = sel_rows is not None and (
    (isinstance(sel_rows, pd.DataFrame) and len(sel_rows) > 0) or
    (isinstance(sel_rows, list) and len(sel_rows) > 0)
)
if has_sel:
    sel_row = sel_rows.iloc[0] if isinstance(sel_rows, pd.DataFrame) else pd.Series(sel_rows[0])
    sp      = int(sel_row.get("_row_idx", 0))
    new_sel = {"pos": sp, "label": f"{sel_row.get('Cliente', '')} — {sel_row.get('Attività', '')}"}
    if st.session_state.sel_info is None:
        st.session_state.sel_info      = new_sel
        st.session_state.work_override = grid_response.data.copy()
        st.rerun()
    else:
        st.session_state.sel_info = new_sel
else:
    st.session_state.sel_info = None

# ── Azione pendente ───────────────────────────────────────────────────────────
edited  = grid_response.data
pending = st.session_state.pending_action

if pending and sel_info is not None:
    sp = sel_info["pos"]
    st.session_state.pending_action = None

    def _make_dup(pos, before=False):
        dup = edited.iloc[pos].to_dict()
        dup["Attività"] = "COPIA - " + str(dup.get("Attività", ""))
        insert_at = pos if before else pos + 1
        nw = pd.concat([edited.iloc[:insert_at],
                        pd.DataFrame([dup]),
                        edited.iloc[insert_at:]], ignore_index=True)
        nw["_row_idx"] = range(len(nw))
        return nw

    if pending == "dup_above":
        nw = _make_dup(sp, before=True)
    elif pending == "dup_below":
        nw = _make_dup(sp, before=False)
    elif pending == "insert":
        blank = {col: "" for col in edited.columns}
        nw = pd.concat([edited.iloc[:sp + 1],
                        pd.DataFrame([blank]),
                        edited.iloc[sp + 1:]], ignore_index=True)
        nw["_row_idx"] = range(len(nw))
    elif pending == "delete":
        nw = pd.concat([edited.iloc[:sp],
                        edited.iloc[sp + 1:]], ignore_index=True)
        nw["_row_idx"] = range(len(nw))
    else:
        nw = None

    if nw is not None:
        st.session_state.work_override = nw
        st.session_state.sel_info      = None
        st.session_state.editor_v     += 1
        st.rerun()

# ── Salvataggio ───────────────────────────────────────────────────────────────
def _do_save():
    other        = df.drop(filtered_index, errors="ignore").copy()
    edited_clean = edited.drop(columns=["_check", "Tipo_Icon", "Stato_Icon", "_row_idx"], errors="ignore")
    merged       = pd.concat([other, edited_clean], ignore_index=True)
    try:
        save_data(merged)
        st.session_state.editor_v     += 1
        st.session_state.work_override = None
        st.success("Salvato!")
        st.rerun()
    except Exception as e:
        from utils.secrets import get_github_token
        t = get_github_token()
        import hashlib
        h = hashlib.md5(t.encode()).hexdigest()[:8] if t else "VUOTO"
        st.error(f"Errore salvataggio (len={len(t)}, md5={h}): {e}")

if save_clicked:
    _do_save()
