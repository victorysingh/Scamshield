"""
orchestrate/deploy.py

One-command deploy script for ScamShield on watsonx Orchestrate.

Usage:
    python orchestrate/deploy.py

Requirements:
    - WATSONX_ORCHESTRATE_API_KEY set in .env or environment
    - WATSONX_ORCHESTRATE_URL set in .env or environment
    - Run from the project root directory

Steps this script performs:
    1. Activate the Orchestrate environment
    2. Import the three tool functions
    3. Deploy the agent from agent.yaml
"""

import os
import subprocess
import sys
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

API_KEY = os.environ.get("WATSONX_ORCHESTRATE_API_KEY", "")
URL     = os.environ.get("WATSONX_ORCHESTRATE_URL", "")

if not API_KEY or not URL:
    print("[ERROR] Set WATSONX_ORCHESTRATE_API_KEY and WATSONX_ORCHESTRATE_URL")
    print("        in a .env file or as environment variables before deploying.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Helper: run an orchestrate CLI command
# ---------------------------------------------------------------------------

_ORCHESTRATE = str(Path(sys.executable).parent / "orchestrate")

def _run(args: list[str]) -> None:
    cmd = [_ORCHESTRATE] + args
    print(f"\n>>> {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"[ERROR] Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


# ---------------------------------------------------------------------------
# Deploy steps
# ---------------------------------------------------------------------------

def main() -> None:
    agent_yaml = str(Path(__file__).parent / "agent.yaml")
    tools_file = str(Path(__file__).parent / "tools" / "scamshield_tools.py")

    # Step 1 — activate environment
    _run([
        "env", "activate",
        "--env-name", "scamshield",
        "--api-key",  API_KEY,
        "--url",      URL,
    ])

    # Step 2 — import tools
    _run(["tools", "import", "python", tools_file])

    # Step 3 — deploy agent
    _run(["agents", "deploy", agent_yaml])

    print("\n[OK] ScamShield agent deployed successfully.")
    print("     Open watsonx Orchestrate and find 'scamshield-agent' in Agents.")


if __name__ == "__main__":
    main()
