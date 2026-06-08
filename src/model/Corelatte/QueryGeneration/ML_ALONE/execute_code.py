import subprocess
import sys
from pathlib import Path


def execute_python_script(
    script_path: Path,
    timeout_seconds: int = 120,
) -> subprocess.CompletedProcess:
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    if script_path.suffix != ".py":
        raise ValueError(f"Expected a Python script, got: {script_path}")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )

    return result


def script_runs_successfully(
    script_path: Path,
    timeout_seconds: int = 120,
) -> bool:
    result = execute_python_script(
        script_path=script_path,
        timeout_seconds=timeout_seconds,
    )

    return result.returncode == 0


def assert_script_runs_successfully(
    script_path: Path,
    timeout_seconds: int = 120,
) -> None:
    result = execute_python_script(
        script_path=script_path,
        timeout_seconds=timeout_seconds,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Generated script failed.\n\n"
            f"Script: {script_path}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )