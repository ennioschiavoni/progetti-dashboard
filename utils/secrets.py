import os
import streamlit as st


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
        return {
            "owner_username": os.environ.get("AUTH_OWNER_USERNAME", ""),
            "owner_password": os.environ.get("AUTH_OWNER_PASSWORD", ""),
            "resp_username":  os.environ.get("AUTH_RESP_USERNAME", ""),
            "resp_password":  os.environ.get("AUTH_RESP_PASSWORD", ""),
            "dev_mode":       os.environ.get("AUTH_DEV_MODE", "false").lower() == "true",
        }


def get_github_token() -> str:
    try:
        return st.secrets["github"]["token"]
    except Exception:
        return os.environ.get("GITHUB_TOKEN", "")
