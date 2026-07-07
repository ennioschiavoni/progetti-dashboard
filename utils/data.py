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
    import base64
    t = _token()
    basic = base64.b64encode(f"ennioschiavoni:{t}".encode("ascii")).decode("ascii")
    return {"Authorization": f"Basic {basic}",
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
    import subprocess, tempfile, os, shutil
    st.cache_data.clear()

    save_df = df.drop(columns=["Tipo_Icon", "Stato_Icon", "_row_idx", "_check"],
                      errors="ignore").copy()

    if len(save_df) < 50:
        raise Exception(f"Sicurezza: il CSV ha solo {len(save_df)} righe — salvataggio annullato per evitare perdita dati.")

    token = _token()
    repo_url = f"https://ennioschiavoni:{token}@github.com/{GITHUB_REPO}.git"

    git_env = os.environ.copy()
    git_env["GIT_TERMINAL_PROMPT"] = "0"
    git_env["GIT_ASKPASS"] = "echo"

    tmpdir = tempfile.mkdtemp()
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", repo_url, tmpdir],
            check=True, capture_output=True, timeout=60, env=git_env
        )
        save_df.to_csv(os.path.join(tmpdir, GITHUB_PATH), index=False)
        subprocess.run(["git", "-C", tmpdir, "config", "user.email", "app@streamlit.io"], check=True, capture_output=True)
        subprocess.run(["git", "-C", tmpdir, "config", "user.name", "Streamlit App"], check=True, capture_output=True)
        subprocess.run(["git", "-C", tmpdir, "add", GITHUB_PATH], check=True, capture_output=True)
        subprocess.run(["git", "-C", tmpdir, "commit", "-m", "Aggiornamento dati progetti"], check=True, capture_output=True)
        subprocess.run(["git", "-C", tmpdir, "push"], check=True, capture_output=True, timeout=60, env=git_env)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Git error: {e.stderr.decode()[:300] if e.stderr else str(e)}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
