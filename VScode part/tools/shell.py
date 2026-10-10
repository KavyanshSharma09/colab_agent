import subprocess

from config import WORKSPACE_DIR


def run_command(command: str):
    """
    Run a shell command inside the agent workspace.
    """

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
            timeout=10,
        )

        return {
            "success": result.returncode == 0,
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 10 seconds.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }