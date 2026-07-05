import os
import subprocess
import sys

os.makedirs(".streamlit", exist_ok=True)

token = os.environ.get("GITHUB_TOKEN", "").strip().strip("\"'")

secrets = f"""[auth]
owner_username = "{os.environ.get('AUTH_OWNER_USERNAME', '')}"
owner_password = "{os.environ.get('AUTH_OWNER_PASSWORD', '')}"
resp_username  = "{os.environ.get('AUTH_RESP_USERNAME', '')}"
resp_password  = "{os.environ.get('AUTH_RESP_PASSWORD', '')}"
dev_mode = false

[github]
token = "{token}"
"""

with open(".streamlit/secrets.toml", "w") as f:
    f.write(secrets)

print(f"secrets.toml created, token length: {len(token)}")

port = os.environ.get("PORT", "10000")
subprocess.run([
    sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
    "--server.port", port,
    "--server.address", "0.0.0.0",
])
