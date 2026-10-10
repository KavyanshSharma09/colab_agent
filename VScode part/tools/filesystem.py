from pathlib import Path

from config import WORKSPACE_DIR


WORKSPACE = Path(WORKSPACE_DIR).resolve()


def safe_path(path: str):
    """
    Resolve a path and make sure it stays inside workspace/.
    """

    file_path = (WORKSPACE / path).resolve()

    try:
        file_path.relative_to(WORKSPACE)
    except ValueError:
        return None

    return file_path


def read_file(path: str):
    """
    Read a text file from the workspace.
    """

    file_path = safe_path(path)

    if file_path is None:
        return {
            "success": False,
            "error": "Access denied."
        }

    if not file_path.exists():
        return {
            "success": False,
            "error": "File does not exist."
        }

    if not file_path.is_file():
        return {
            "success": False,
            "error": "Path is not a file."
        }

    try:
        content = file_path.read_text(encoding="utf-8")

        return {
            "success": True,
            "path": path,
            "content": content
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Could not read file: {e}"
        }


def write_file(path: str, content: str):
    """
    Create or overwrite a text file inside the workspace.
    """

    file_path = safe_path(path)

    if file_path is None:
        return {
            "success": False,
            "error": "Access denied."
        }

    try:
        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        return {
            "success": True,
            "message": f"Successfully wrote {path}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Could not write file: {e}"
        }


def list_files():
    """
    List all files inside the workspace.
    """

    try:
        files = []

        for file in WORKSPACE.rglob("*"):
            if file.is_file():
                files.append(
                    str(file.relative_to(WORKSPACE))
                )

        return {
            "success": True,
            "files": files
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Could not list files: {e}"
        }