from pathlib import Path

from config import WORKSPACE_DIR


WORKSPACE = Path(WORKSPACE_DIR).resolve()


def search_code(query: str):
    """
    Search for a text string inside files in the workspace.
    """

    results = []

    for file in WORKSPACE.rglob("*"):

        if not file.is_file():
            continue

        try:
            content = file.read_text(
                encoding="utf-8"
            )

            for line_number, line in enumerate(
                content.splitlines(),
                start=1
            ):

                if query.lower() in line.lower():

                    results.append({
                        "file": str(
                            file.relative_to(WORKSPACE)
                        ),
                        "line": line_number,
                        "content": line.strip(),
                    })

        except Exception:
            # Ignore binary/unreadable files
            continue

    if not results:
        return {
            "success": True,
            "matches": []
        }

    return {
        "success": True,
        "matches": results
    }