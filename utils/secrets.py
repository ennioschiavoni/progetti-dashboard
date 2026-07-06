import os
import streamlit as st

try:
    import tomllib
except ImportError:
    tomllib = None

RENDER_SECRETS = "/etc/secrets/secrets.toml"


def _load_render_secrets() -> dict:
    if tomllib is None:
        return {}
    try:
        with open(RENDER_SECRETS, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def get_auth() -> dict:
    try:
        s = st.secrets["auth"]
        return {
            "owner_username": s["owner_username"],
            "owner_password": s["owner_password"],
            "resp_username":  s["resp_username"],
            "resp_password":  s["resp_password"],
            "dev_mode":       s.get("dev_mode", False),
        }
    except Exception:
        pass

    r = _load_render_secrets().get("auth", {})
    if r:
        return {
            "owner_username": r.get("owner_username", ""),
            "owner_password": r.get("owner_password", ""),
            "resp_username":  r.get("resp_username", ""),
            "resp_password":  r.get("resp_password", ""),
            "dev_mode":       r.get("dev_mode", False),
        }

    return {
        "owner_username": os.environ.get("AUTH_OWNER_USERNAME", ""),
        "owner_password": os.environ.get("AUTH_OWNER_PASSWORD", ""),
        "resp_username":  os.environ.get("AUTH_RESP_USERNAME", ""),
        "resp_password":  os.environ.get("AUTH_RESP_PASSWORD", ""),
        "dev_mode":       os.environ.get("AUTH_DEV_MODE", "false").lower() == "true",
    }


def get_github_token() -> str:
    try:
        return st.secrets["github_pat"]["token"]
    except Exception:
        pass
    try:
        return st.secrets["github"]["token"]
    except Exception:
        pass

    token = _load_render_secrets().get("github", {}).get("token", "")
    if token:
        return token

    return os.environ.get("GITHUB_TOKEN", "").strip()
