import base64
import io
import pandas as pd
import requests
import streamlit as st

GITHUB_REPO  = "ennioschiavoni/progetti-data"
GITHUB_PATH  = "progetti.csv"
GITHUB_API   = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}"
RAW_URL      = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}"

RESP_ALIASES = {
    "Danile Garaffo":  "Daniele Garaffo",
    "Caludio Tonti":   "Claudio Tonti",
    "Enico Gualandi":  "Enrico Gualandi",
}

SORT_COLS = {
    "Ordina per Cliente":         "Cliente",
    "Ordina per Project Manager": "Resp.Progetto",
    "Ordina per Tipo Attività":   "Tipo Attività",
    "Ordina per Stato Attività":  "Stato Attività",
    "Ordina per TR/PR":           "TR_PR",
}

PM_EDITABLE_COLS = [
    "Tipo Attività",
    "Stato Attività",
    "Stato_Resp",
    "Note Ennio",
    "Next Step COM",
]

TIPO_OPTIONS = [
    "Presale Cliente",
    "Presale Prospect",
    "On-going",
    "Accettata",
    "Interna",
]

STATO_OPTIONS = [
    "Critica",
    "Verifica Cliente",
    "Verifica PM",
    "Chiusa",
]

TIPO_COLORS = {
    "Presale Cliente":  "🟣",
    "Presale Prospect": "🔵",
    "On-going":         "🟡",
    "Accettata":        "⚫",
    "Interna":          "🟢",
}

STATO_COLORS = {
    "Critica":          "🔴",
    "Verifica Cliente": "🔵",
    "Verifica PM":      "🟠",
    "Chiusa":           "⚫",
}


def _token() -> str:
    from utils.secrets import get_github_token
    t = get_github_token().strip()
    return t.encode("ascii", errors="ignore").decode("ascii")


def _headers() -> dict:
    return {"Authorization": f"token {_token()}",
            "Accept": "application/vnd.github.v3+json"}


@st.cache_data(ttl=10)
def load_data() -> pd.DataFrame:
    resp = requests.get(RAW_URL, timeout=15)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text))

    df["Cliente"] = df["Cliente"].ffill()
    df["Resp.Progetto"] = df["Resp.Progetto"].replace(RESP_ALIASES)
    if "Tipo Attività" in df.columns:
        df["Tipo Attività"] = df["Tipo Attività"].replace({"Ongoing": "On-going"})
    if "Stato Attività" in df.columns:
        df["Stato Attività"] = df["Stato Attività"].replace({"Critico": "Critica"})
    for col in ["Stato_Resp", "Note Ennio", "Next Step COM", "Tipo Attività", "Stato Attività"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip().replace("nan", "")
    df["TR_PR"] = df["TR_PR"].fillna("").astype(str).str.strip().replace("\xa0", "").replace("nan", "")
    df["Tipo_Icon"]  = df["Tipo Attività"].map(TIPO_COLORS).fillna("⚪")
    df["Stato_Icon"] = df["Stato Attività"].map(STATO_COLORS).fillna("⚪")
    df = df.dropna(subset=["Attività"])
    df = df.reset_index(drop=True)
    return df


def save_data(df: pd.DataFrame):
    st.cache_data.clear()

    save_df = df.drop(columns=["Tipo_Icon", "Stato_Icon", "_row_idx", "_check"],
                      errors="ignore").copy()

    csv_content = save_df.to_csv(index=False)
    csv_b64 = base64.b64encode(csv_content.encode()).decode()

    # Recupera SHA del file attuale (necessario per aggiornarlo via API)
    meta = requests.get(GITHUB_API, headers=_headers(), timeout=10)
    sha = meta.json().get("sha", "")

    payload = {
        "message": "Aggiornamento dati progetti",
        "content": csv_b64,
        "sha": sha,
        "branch": "main",
    }
    r = requests.put(GITHUB_API, headers=_headers(), json=payload, timeout=20)
    r.raise_for_status()
