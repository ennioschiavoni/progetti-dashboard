import json
from pathlib import Path

PREFS_DIR = Path(__file__).parent.parent / "data"

DASHBOARD_DEFAULTS = {
    "Tipo":           True,
    "Stato":          True,
    "Cliente":        True,
    "Attività":       True,
    "Tipo Attività":  True,
    "Stato Attività": True,
    "Project Manager":          True,
    "Stato (PM)":  True,
    "Note Ennio":     True,
    "Next Step":      True,
    "TR/PR":          True,
    "Rilascio":       True,
    "Data SAL":       True,
    "PM":             True,
    "Owner":          True,
}

MODIFICA_DEFAULTS = {k: True for k in DASHBOARD_DEFAULTS}

COLUMN_DEFAULTS = DASHBOARD_DEFAULTS  # alias per compatibilità sidebar


def _path(page: str) -> Path:
    return PREFS_DIR / f"prefs_{page}.json"


def load_prefs(page: str = "dashboard") -> dict:
    defaults = MODIFICA_DEFAULTS if page == "modifica" else DASHBOARD_DEFAULTS
    path = _path(page)
    if path.exists():
        try:
            saved = json.loads(path.read_text())
            return {k: saved.get(k, v) for k, v in defaults.items()}
        except Exception:
            pass
    return dict(defaults)


def save_prefs(prefs: dict, page: str = "dashboard"):
    _path(page).write_text(json.dumps(prefs, ensure_ascii=False, indent=2))


COL_ORDER_DEFAULT = [
    "Stato Attività", "Tipo Attività", "Cliente", "Project Manager",
    "Attività", "Stato (PM)", "Note Ennio", "Next Step",
    "TR/PR", "Rilascio", "Data SAL", "PM", "Owner",
]


def _order_path(page: str) -> Path:
    return PREFS_DIR / f"col_order_{page}.json"


def load_col_order(page: str = "dashboard") -> list:
    path = _order_path(page)
    if path.exists():
        try:
            saved = json.loads(path.read_text())
            known = set(COL_ORDER_DEFAULT)
            result = [c for c in saved if c in known]
            for c in COL_ORDER_DEFAULT:
                if c not in result:
                    result.append(c)
            return result
        except Exception:
            pass
    return list(COL_ORDER_DEFAULT)


def save_col_order(order: list, page: str = "dashboard"):
    _order_path(page).write_text(json.dumps(order, ensure_ascii=False, indent=2))
