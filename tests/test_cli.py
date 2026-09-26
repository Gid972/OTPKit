import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

def test_cli_version_and_secret_commands():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(
        [sys.executable, "-m", "otpkit.cli", "version"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
        cwd=str(ROOT),
    )
    assert result.returncode == 0
    assert result.stdout.strip()

    result = subprocess.run(
        [sys.executable, "-m", "otpkit.cli", "secret"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
        cwd=str(ROOT),
    )
    assert result.returncode == 0
    assert result.stdout.strip()
