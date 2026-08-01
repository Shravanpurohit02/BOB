import os
import subprocess
import sys

NAME = "CLI"
CATEGORY = "Foundation"
DESCRIPTION = "Validates the Builder command-line interface."


def run() -> bool:

    try:
        cmd = [
            sys.executable,
            "-m",
            "builder",
            "status",
        ]

        proc = subprocess.run(
            cmd,
            env={
                "PYTHONPATH": ".builder",
                **os.environ,
            },
            capture_output=True,
            text=True,
        )

        return proc.returncode == 0 and "VIDHI BUILDER STATUS" in proc.stdout

    except Exception:
        return False
