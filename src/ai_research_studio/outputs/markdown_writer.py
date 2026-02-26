from pathlib import Path


def write_markdown(file_path: Path, content: str) -> Path:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return file_path