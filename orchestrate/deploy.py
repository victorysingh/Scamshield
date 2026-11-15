"""
orchestrate/deploy.py

One-command deploy script for ScamShield on watsonx Orchestrate.

Usage:
    python orchestrate/deploy.py

Requirements:
    - WXO_API_KEY set in .env or environment
    - WXO_URL set in .env or environment
    - Run from the project root directory

Steps this script performs:
    1. Register + activate the Orchestrate environment
    2. Import the three tool functions
    3. Import the agent from agent.yaml
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Load .env if present (never print its contents)
# ---------------------------------------------------------------------------

_ENV_FILE = Path(__file__).parent.parent / ".env"
if _ENV_FILE.exists():
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

# Support both env var names
API_KEY = os.environ.get("WXO_API_KEY") or os.environ.get("WATSONX_ORCHESTRATE_API_KEY", "")
URL     = os.environ.get("WXO_URL") or os.environ.get("WATSONX_ORCHESTRATE_URL", "")

if not API_KEY:
    print("[ERROR] Set WXO_API_KEY in your .env file before deploying.")
    sys.exit(1)
if not URL:
    print("[ERROR] Set WXO_URL in your .env file before deploying.")
    print("        Example: WXO_URL=https://api.us-east-1.watson-orchestrate.ibm.com/instances/<id>")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Helper: run an orchestrate CLI command
# ---------------------------------------------------------------------------

_ORCHESTRATE = str(Path(sys.executable).parent / "orchestrate")
_PROJECT_ROOT = Path(__file__).parent.parent


def _run(args: list[str], answer: str | None = None) -> None:
    """Run an orchestrate command. *answer* is fed to any y/n prompt."""
    cmd = [_ORCHESTRATE] + args
    # Mask the key so it never lands in a terminal log or screen recording
    shown = ["****" if a == API_KEY else a for a in cmd]
    print(f"\n>>> {' '.join(shown)}")
    result = subprocess.run(cmd, check=False, input=answer, text=answer is not None)
    if result.returncode != 0:
        print(f"[ERROR] Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def _stage_tool_bundle(dest: Path) -> Path:
    """
    Copy only the Python files the tools need into *dest*.

    `tools import --package-root` zips EVERY file under the root, hidden files
    included, so pointing it at the project would upload .env, .git, .venv and
    node_modules. Staging a clean folder keeps credentials out of the upload.
    """
    for rel in ("tools", "orchestrate/tools"):
        (dest / rel).mkdir(parents=True, exist_ok=True)
        for src in (_PROJECT_ROOT / rel).glob("*.py"):
            shutil.copy2(src, dest / rel / src.name)
    shutil.copy2(_PROJECT_ROOT / "orchestrate" / "__init__.py", dest / "orchestrate" / "__init__.py")

    # The runtime only needs the ADK for the @tool decorator — not pytest/flask
    reqs = dest / "requirements.txt"
    reqs.write_text("ibm-watsonx-orchestrate>=2.20.0\n", encoding="utf-8")
    return reqs


# ---------------------------------------------------------------------------
# Deploy steps
# ---------------------------------------------------------------------------

def main() -> None:
    agent_yaml = str(Path(__file__).parent / "agent.yaml")

    # Step 1 — register the environment; answers "Y" if it asks to update an existing one
    _run(["env", "add", "--name", "scamshield", "--url", URL], answer="Y\n")

    # Step 2 — activate it with the API key
    _run(["env", "activate", "scamshield", "--api-key", API_KEY])

    # Step 3 — import tools from a clean staged bundle (see _stage_tool_bundle)
    with tempfile.TemporaryDirectory(prefix="scamshield_bundle_") as tmp:
        bundle = Path(tmp)
        reqs = _stage_tool_bundle(bundle)
        _run([
            "tools", "import",
            "--kind", "python",
            "--file", str(bundle / "orchestrate" / "tools" / "scamshield_tools.py"),
            "--requirements-file", str(reqs),
            "--package-root", str(bundle),
        ])

    # Step 4 — import the agent definition (creates or updates it)
    _run(["agents", "import", "--file", agent_yaml])

    print("\n[OK] ScamShield agent deployed successfully.")
    print("     Open watsonx Orchestrate and find 'scamshield-agent' in Agents.")


if __name__ == "__main__":
    main()
